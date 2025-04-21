import abc
import datetime as dt
import importlib.util  # Added import
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Union

# Huey imports for dynamic config generation and type hints
from huey import (
    FileHuey,
    Huey,
    MemoryHuey,  # Added Huey base class
    PriorityRedisExpireHuey,
    PriorityRedisHuey,
    RedisExpireHuey,
    RedisHuey,
    SqliteHuey,
)
from redis import ConnectionPool

from ...fs import AbstractFileSystem
from ..base import (
    BackendType,
    BaseBackend,
    BaseTrigger,  # Added BackendType
    BaseWorker,
)


class HueyWorker(BaseWorker):
    """
    Huey worker implementation for FlowerPower.
    """

    def __init__(
        self,
        name: str | None = None,
        base_dir: str | None = None,
        backend: BaseBackend | None = None,
        storage_options: dict[str, Any] = None,
        fs: AbstractFileSystem | None = None,
        **kwargs,
    ):
        super().__init__(name, base_dir, backend, storage_options, fs, **kwargs)
        self._worker_processes: list[subprocess.Popen] = []

        # Determine config file path: {base_dir}/.flowerpower/huey_config_{name}.py
        config_dir = Path(self._base_dir) / ".flowerpower"
        # Ensure the directory exists using the provided filesystem abstraction
        self._fs.makedirs(str(config_dir), exist_ok=True)

        config_name = f"huey_config_{self.name or 'default'}.py"
        self._huey_config_path = str(config_dir / config_name)

        self._huey_instance: Optional[Huey] = None  # Will be lazily loaded
        self._create_huey_config_file()

    def _get_huey_instance(self) -> Huey:
        """
        Lazily load and return the Huey instance from the generated config file.
        """
        if self._huey_instance is not None:
            return self._huey_instance

        config_path = Path(self._huey_config_path)
        if not self._fs.exists(str(config_path)):
            # Attempt to recreate if missing (e.g., deleted manually)
            self._create_huey_config_file()
            if not self._fs.exists(str(config_path)):
                raise FileNotFoundError(
                    f"Huey config file could not be found or created: {self._huey_config_path}"
                )

        # Dynamically import the config file and get the 'huey' variable
        module_name = config_path.stem
        spec = importlib.util.spec_from_file_location(module_name, str(config_path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for {self._huey_config_path}")

        # Temporarily add the config directory to sys.path for import
        config_dir = str(config_path.parent)
        original_sys_path = list(sys.path)
        if config_dir not in sys.path:
            sys.path.insert(0, config_dir)

        module = importlib.util.module_from_spec(spec)
        # sys.modules[module_name] = module # Avoid polluting sys.modules if possible

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            # Restore sys.path before raising
            sys.path = original_sys_path
            raise ImportError(
                f"Failed to import Huey config from {self._huey_config_path}: {e}"
            )
        finally:
            # Ensure sys.path is restored
            sys.path = original_sys_path

        if not hasattr(module, "huey"):
            raise AttributeError(
                f"'huey' variable not found in {self._huey_config_path}"
            )

        self._huey_instance = getattr(module, "huey")
        if not isinstance(self._huey_instance, Huey):
            raise TypeError(
                f"Variable 'huey' in {self._huey_config_path} is not a Huey instance."
            )

        return self._huey_instance

    def add_job(
        self,
        func: Callable,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        result_ttl: Union[float, dt.timedelta] = 0,
        **job_kwargs,
    ) -> str:
        """
        Add a one-off job to the Huey queue.
        """
        # TODO: Implement using Huey API
        # Need to handle mapping func to a Huey task if not already decorated
        # Need to handle result_ttl -> Huey's result expiration?
        # Need to handle job_kwargs (priority, retries, etc.)
        huey = self._get_huey_instance()
        generic_task_wrapper = getattr(huey, "generic_huey_task")

        module_path, function_name = self._get_function_path(func)

        huey_options = {
            k: job_kwargs.pop(k)
            for k in ("priority", "retries", "retry_delay")
            if k in job_kwargs
        }

        task_instance = generic_task_wrapper.s(
            module_path, function_name, args or (), kwargs or {}
        ).options(**huey_options)
        result = huey.enqueue(task_instance)
        return result.id

    def add_schedule(
        self,
        func: Callable,
        trigger: "BaseTrigger",
        id: Optional[str] = None,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        **schedule_kwargs,
    ) -> str:
        """
        Add a scheduled (recurring or one-off future) job using Huey.
        """
        # TODO: Implement using Huey API
        # Need to map BaseTrigger to Huey's crontab or delay/eta
        # Need to handle mapping func to a Huey task
        # Need to handle schedule_kwargs
        huey = self._get_huey_instance()
        generic_task_wrapper = getattr(huey, "generic_huey_task")

        module_path, function_name = self._get_function_path(func)

        trigger_instance = trigger.get_trigger_instance()
        huey_schedule_options = trigger_instance

        # Combine schedule_kwargs with eta/delay options
        huey_schedule_options.update(
            {
                k: schedule_kwargs.pop(k)
                for k in ("priority", "retries", "retry_delay")
                if k in schedule_kwargs
            }
        )

        result = generic_task_wrapper.schedule(
            args=(module_path, function_name, args or (), kwargs or {}),
            **huey_schedule_options,
        )
        return result.id

    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a scheduled job by its ID.
        Huey's revocation might be based on task definition or specific instance.
        """
        huey = self._get_huey_instance()
        try:
            # TODO: If schedule_id refers to a periodic task definition, this might need to revoke the entire periodic task.
            return huey.revoke_by_id(schedule_id, revoke_once=True)
        except Exception as e:
            print(f"Error removing schedule {schedule_id}: {e}")
            return False

    def remove_all_schedules(self) -> None:
        """
        Remove all scheduled jobs.
        """
        huey = self._get_huey_instance()
        try:
            huey.storage.flush_schedule()
        except Exception as e:
            print(f"Error removing all schedules: {e}")

    def get_job_result(self, job_id: str) -> Any:
        """
        Retrieve the result of a completed job by its job ID.
        """
        huey = self._get_huey_instance()
        try:
            return huey.result(job_id, preserve=True)
        except Exception as e:
            print(f"Error getting result for job {job_id}: {e}")
            return None

    def get_schedules(self, as_dict: bool = False) -> list:
        """
        Get a list of all scheduled jobs from Huey.
        """
        huey = self._get_huey_instance()
        try:
            scheduled_tasks = huey.scheduled()
            # TODO: Format these as dicts if as_dict is True
            return list(scheduled_tasks)
        except Exception as e:
            print(f"Error getting schedules: {e}")
            return []

    def get_jobs(self, as_dict: bool = False) -> list:
        """
        Get a list of all jobs (pending in queue).
        """
        huey = self._get_huey_instance()
        try:
            pending_tasks = huey.pending()
            # TODO: Format these as dicts if as_dict is True
            return list(pending_tasks)
        except Exception as e:
            print(f"Error getting jobs: {e}")
            return []

    def show_schedules(self) -> None:
        """
        Print or log all current schedules.
        """
        schedules = self.get_schedules()
        print("Scheduled Tasks:")
        if schedules:
            for schedule in schedules:
                print(
                    f"- Task ID: {schedule.id}, ETA: {schedule.eta}"
                )  # Improved format
            # TODO: More detailed formatting (function name, args)
        else:
            print("  No scheduled tasks.")

    def show_jobs(self) -> None:
        """
        Print or log all current jobs in the queue.
        """
        jobs = self.get_jobs()
        print("Pending Jobs in Queue:")
        if jobs:
            for job in jobs:
                print(f"- Task ID: {job.id}")  # Improved format
            # TODO: More detailed formatting (function name, args, priority)
        else:
            print("  Queue is empty.")

    def _start_consumer_process(self, worker_args: list[str]):
        """Helper to start a huey_consumer.py process."""
        command = [
            sys.executable,
            "-m",
            "huey.bin.huey_consumer",
            self._get_huey_instance_path(),
        ]
        command.extend(worker_args)

        cwd = self._base_dir
        print(f"Starting Huey consumer with command: {' '.join(command)} in {cwd}")
        try:
            process = subprocess.Popen(command, cwd=cwd)
            self._worker_processes.append(process)
            print(f"Huey consumer started (PID: {process.pid})")
        except Exception as e:
            print(f"Error starting Huey consumer: {e}")

    def start_worker(self, background: bool = False) -> None:
        """
        Start a single Huey worker process.
        """
        if self._worker_processes:
            print("Worker already running.")
            return

        print("Starting single Huey worker...")
        worker_args = ["-w", "1", "-k", "thread"]  # Default args for single worker
        self._start_consumer_process(worker_args)
        print("Worker started in background.")  # Popen is background

    def stop_worker(self) -> None:
        """
        Stop the single Huey worker process.
        """
        print("Stopping Huey worker(s)...")
        for process in self._worker_processes:
            try:
                print(f"Sending SIGINT to PID {process.pid}...")
                process.send_signal(subprocess.SIGINT)  # Graceful shutdown
                process.wait(timeout=10)  # Wait for graceful shutdown
                print(f"Process {process.pid} terminated gracefully.")
            except subprocess.TimeoutExpired:
                print(
                    f"Process {process.pid} did not terminate gracefully, sending SIGTERM..."
                )
                process.terminate()  # Force kill
                process.wait()
                print(f"Process {process.pid} terminated.")
            except Exception as e:
                print(f"Error stopping process {process.pid}: {e}")

        self._worker_processes = []
        print("Huey worker(s) stopped.")

    def start_worker_pool(
        self, num_workers: int = None, background: bool = True
    ) -> None:
        """
        Start a pool of Huey workers.
        """
        if self._worker_processes:
            print("Worker pool already running.")
            return

        num_workers = num_workers or os.cpu_count() or 1
        worker_type = "thread"  # Default worker type, TODO: config
        print(f"Starting Huey worker pool ({num_workers} {worker_type} workers)...")
        worker_args = ["-w", str(num_workers), "-k", worker_type]
        self._start_consumer_process(worker_args)
        print("Worker pool started in background.")  # Popen is background

    def stop_worker_pool(self) -> None:
        """
        Stop all Huey worker processes in the pool.
        """
        self.stop_worker()

    def _create_huey_config_file(self):
        """
        Generate a Python config file that instantiates a Huey instance
        based on the backend configuration.
        """
        backend = self._backend
        name = self.name or "flowerpower_huey"  # Huey needs a name
        config_lines = [
            "from huey import RedisHuey, SqliteHuey, PriorityRedisHuey, RedisExpireHuey, PriorityRedisExpireHuey, FileHuey, MemoryHuey",
            "from redis import ConnectionPool",
            "import os",
            "",
        ]

        # Defensive: handle both enum and str for backend.type
        backend_type = getattr(backend, "type", None)
        if isinstance(backend_type, str):
            backend_type_str = backend_type.lower()
        elif isinstance(backend_type, BackendType):
            backend_type_str = backend_type.value
        else:
            backend_type_str = "memory"  # Default to memory if type is missing

        # Redis backend
        if backend_type_str == "redis":
            # Use URI if provided, else build from host/port/db/user/pass
            uri = getattr(backend, "uri", None)
            host = getattr(backend, "host", "localhost")
            port = getattr(backend, "port", 6379)
            db = getattr(backend, "database", 0)  # Redis DB is usually an int
            username = getattr(backend, "username", None)
            password = getattr(backend, "password", None)
            ssl = getattr(backend, "ssl", False)

            # ConnectionPool args
            pool_args = [
                f"host='{host}'",
                f"port={port}",
                f"db={int(db)}",  # Ensure db is int
            ]
            if username:
                pool_args.append(f"username='{username}'")
            if password:
                pool_args.append(f"password='{password}'")
            if ssl:
                pool_args.append("ssl=True")
                # Add other SSL options if needed, e.g., ssl_cert_reqs='required'
                # pool_args.append("ssl_cert_reqs='none'") # Example: disable cert verification if needed

            config_lines.append(f"pool = ConnectionPool({', '.join(pool_args)})")
            # TODO: Add support for PriorityRedisHuey etc. based on config?
            config_lines.append(f"huey = RedisHuey('{name}', connection_pool=pool)")
            # Sqlite backend
        elif backend_type_str == "sqlite":
            # Database path should be relative to base_dir or absolute
            db_path_str = getattr(backend, "database", f"{name}.db")
            db_path = Path(db_path_str)
            if not db_path.is_absolute():
                # Assume relative to base_dir if not absolute
                db_path = Path(self._base_dir) / db_path
            # Ensure the directory for the SQLite file exists
            db_dir = db_path.parent
            if not self._fs.exists(str(db_dir)):
                self._fs.makedirs(str(db_dir), exist_ok=True)

            config_lines.append(
                f"db_file = r'{str(db_path)}'"
            )  # Use raw string for Windows paths
            config_lines.append(f"huey = SqliteHuey('{name}', filename=db_file)")

            # File backend (useful for simple local testing)
        elif backend_type_str == "file":
            file_path_str = getattr(
                backend, "database", f"{name}_huey_storage"
            )  # Use 'database' field for path convention
            file_path = Path(file_path_str)
            if not file_path.is_absolute():
                file_path = Path(self._base_dir) / ".flowerpower" / file_path
            # Ensure directory exists
            file_dir = file_path.parent
            if not self._fs.exists(str(file_dir)):
                self._fs.makedirs(str(file_dir), exist_ok=True)
            config_lines.append(f"storage_path = r'{str(file_path)}'")
            config_lines.append(f"huey = FileHuey('{name}', path=storage_path)")

            # Memory backend (default)
        else:  # Default to MemoryHuey
            config_lines.append(f"huey = MemoryHuey('{name}')")

            # Add generic Huey task definition
            config_lines.extend(
                [
                    "import importlib",
                    "",
                    "@huey.task(context=True)",
                    "def generic_huey_task(module_path, function_name, args, kwargs, task=None):",
                    '    """Generic Huey task to execute an arbitrary function."""',
                    "    try:",
                    "        module = importlib.import_module(module_path)",
                    "        func_to_run = getattr(module, function_name)",
                    "        print(f\"Executing {module_path}.{function_name} via Huey task {task.id if task else 'N/A'}\")",
                    "        return func_to_run(*args, **kwargs)",
                    "    except Exception as e:",
                    '        print(f"Error in generic_huey_task executing {module_path}.{function_name}: {e}")',
                    "        raise # Re-raise the exception so Huey handles retries/errors",
                    "",
                ]
            )
            config_content = "\n".join(config_lines)
            try:
                self._fs.write_text(self._huey_config_path, config_content)
                print(f"Generated Huey config: {self._huey_config_path}")
            except Exception as e:
                print(f"Error writing Huey config file {self._huey_config_path}: {e}")
                raise  # Re-raise the exception

        def _get_huey_instance_path(self) -> str:
            """
            Return the Python import path for the huey instance in the config file.
            Example: '.flowerpower.huey_config_default.huey' if base_dir is in sys.path
            or just 'huey_config_default.huey' if the .flowerpower dir is added to sys.path.
            The consumer needs this path.
            """
            config_path = Path(self._huey_config_path)
            # We assume the directory containing the config file will be added to sys.path
            # by the consumer process or the environment setup.
            module_name = config_path.stem
            return f"{module_name}.huey"

        # --- Context Manager ---
        def __enter__(self):
            # Optional: Start worker/pool on entering context?
            # self.start_worker(background=True) # Example
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            # Ensure workers are stopped on exiting context
            self.stop_worker()  # Handles both single and pool

        def _get_function_path(self, func: Callable) -> tuple[str, str]:
            """
            Helper method to reliably get the module path and function name.
            """
            module_path = func.__module__
            function_name = func.__name__
            return module_path, function_name
