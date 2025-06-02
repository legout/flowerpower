import datetime as dt
import os
import posixpath
from pathlib import Path

import rich
from loguru import logger

from . import settings
from .cfg import ProjectConfig
from .fs import (AbstractFileSystem, BaseStorageOptions, DirFileSystem,
                 get_filesystem)
from .job_queue import JobQueueManager
from .pipeline import PipelineManager
from .utils.logging import setup_logging

setup_logging(level=settings.LOG_LEVEL)


class FlowerPowerProject:
    def __init__(
        self,
        pipeline_manager: PipelineManager,
        job_queue_manager: JobQueueManager | None = None,
    ):
        """
        Initialize a FlowerPower project.
        Args:
            pipeline_manager (PipelineManager | None): Instance of PipelineManager to manage pipelines.
            job_queue_manager (JobQueueManager | None): Instance of JobQueueManager to manage job queues.
        """
        self.pipeline_manager = pipeline_manager
        self.job_queue_manager = job_queue_manager
        self.name = self.pipeline_manager.project_cfg.name
        self._base_dir = self.pipeline_manager._base_dir
        self._fs = self.pipeline_manager._fs
        self._storage_options = self.pipeline_manager._storage_options
        self._cfg_dir = self.pipeline_manager._cfg_dir
        self._pipelines_dir = self.pipeline_manager._pipelines_dir
        self.job_queue_type = (
            self.job_queue_manager.cfg.type
            if self.job_queue_manager is not None
            else None
        )
        self.job_queue_backend = (
            self.job_queue_manager.cfg.backend
            if self.job_queue_manager is not None
            else None
        )

    @staticmethod
    def _check_project_exists(base_dir: str, fs: AbstractFileSystem | None = None):
        if fs is None:
            fs = get_filesystem(base_dir, dirfs=True)
        if isinstance(fs, DirFileSystem):
            if not fs.exists("."):
                rich.print(
                    "[red]Project directory does not exist. Please initialize it first.[/red]"
                )
                return False
            if not fs.exists("conf") or not fs.exists("pipelines"):
                rich.print(
                    "[red]Project configuration or pipelines directory is missing[/red]"
                )
                return False
        else:
            if not fs.exists(base_dir):
                rich.print(
                    "[red]Project directory does not exist. Please initialize it first.[/red]"
                )
                return False
            if not fs.exists(posixpath.join(base_dir, "conf")) or not fs.exists(
                posixpath.join(base_dir, "pipelines")
            ):
                rich.print(
                    "[red]Project configuration or pipelines directory is missing[/red]"
                )
                return False

        logger.debug(f"Project exists at {base_dir}")
        return True

    @classmethod
    def load(
        cls,
        base_dir: str | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
        fs: AbstractFileSystem | None = None,
        log_level: str | None = None,
    ) -> "FlowerPowerProject":
        """
        Load an existing FlowerPower project.
        If the project does not exist, it will raise an error.

        Args:
            base_dir (str | None): The base directory of the project. If None, it defaults to the current working directory.
            storage_options (dict | BaseStorageOptions | None): Storage options for the filesystem.
            fs (AbstractFileSystem | None): An instance of AbstractFileSystem to use for file operations.
            log_level (str | None): The logging level to set for the project. If None, it uses the default log level.

        Returns:
            FlowerPowerProject: An instance of FlowerPowerProject if the project exists, otherwise None.
        Raises:
            FileNotFoundError: If the project does not exist at the specified base directory.
        """
        if log_level:
            setup_logging(level=log_level)

        base_dir = base_dir or str(Path.cwd())

        if storage_options is not None:
            cached = True
            cache_storage = posixpath.join(
                posixpath.expanduser(settings.CACHE_DIR), base_dir.split("://")[-1]
            )
            os.makedirs(cache_storage, exist_ok=True)
        else:
            cached = False
            cache_storage = None
        if not fs:
            fs = get_filesystem(
                base_dir,
                storage_options=storage_options,
                cached=cached,
                cache_storage=cache_storage,
            )

        if cls._check_project_exists(base_dir, fs):
            logger.info(f"Loading FlowerPower project from {base_dir}")
            pipeline_manager = PipelineManager(
                base_dir=base_dir,
                storage_options=storage_options,
                fs=fs,
                log_level=log_level,
            )

            job_queue_manager = JobQueueManager(
                storage_options=storage_options,
                fs=fs,
                log_level=log_level,
            )
            return cls(
                pipeline_manager=pipeline_manager,
                job_queue_manager=job_queue_manager,
            )
        else:
            logger.error(
                f"Project does not exist at {base_dir}. Please initialize it first. Use `FlowerPowerProject.init()` to create a new project."
            )
            return None

    @classmethod
    def init(
        cls,
        name: str | None = None,
        base_dir: str | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
        fs: AbstractFileSystem | None = None,
        job_queue_type: str = settings.JOB_QUEUE_TYPE,
        cfg_dir: str = settings.CONFIG_DIR,
        pipelines_dir: str = settings.PIPELINES_DIR,
        hooks_dir: str = settings.HOOKS_DIR,
        log_level: str | None = None,
    ) -> "FlowerPowerProject":
        """
        Initialize a new FlowerPower project.

        Args:
            name (str | None): The name of the project. If None, it defaults to the current directory name.
            base_dir (str | None): The base directory where the project will be created. If None, it defaults to the current working directory.
            storage_options (dict | BaseStorageOptions | None): Storage options for the filesystem.
            fs (AbstractFileSystem | None): An instance of AbstractFileSystem to use for file operations.
            job_queue_type (str): The type of job queue to use for the project.
            cfg_dir (str): The directory where the project configuration will be stored.
            pipelines_dir (str): The directory where the project pipelines will be stored.
            hooks_dir (str): The directory where the project hooks will be stored.
        Returns:
            FlowerPowerProject: An instance of FlowerPowerProject initialized with the new project.
        Raises:
            FileExistsError: If the project already exists at the specified base directory.
        """
        if log_level:
            setup_logging(level=log_level)

        if name is None:
            name = str(Path.cwd().name)
            base_dir = posixpath.join(str(Path.cwd().parent), name)

        if base_dir is None:
            base_dir = posixpath.join(str(Path.cwd()), name)

        if fs is None:
            fs = get_filesystem(
                path=base_dir,
                dirfs=True,
                storage_options=storage_options,
            )

        fs.makedirs(f"{cfg_dir}/pipelines", exist_ok=True)
        fs.makedirs(pipelines_dir, exist_ok=True)
        fs.makedirs(hooks_dir, exist_ok=True)

        cfg = ProjectConfig.load(name=name, job_queue_type=job_queue_type, fs=fs)

        with fs.open("README.md", "w") as f:
            f.write(
                f"# FlowerPower project {name.replace('_', ' ').upper()}\n\n"
                f"**created on**\n\n*{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            )
        cfg.save(fs=fs)
        os.chdir(posixpath.join(base_dir, name))

        rich.print(
            f"\n✨ Initialized FlowerPower project [bold blue]{name}[/bold blue] "
            f"at [italic green]{base_dir}[/italic green]\n"
        )

        rich.print(
            """[bold yellow]Getting Started:[/bold yellow]

0. 🔧 [bold white]Optional: Install uv project manager[/bold white]
    It is recommended to use the python project manager [bold cyan]`uv`[/bold cyan] to manage the
    dependencies of your FlowerPower project.

    Install uv:
        [dim]Run:[/dim] [bold white]pip install uv[/bold white]
        [dim]More options:[/dim] [blue underline]https://docs.astral.sh/uv/getting-started/installation/[/blue underline]

    Initialize uv in your flowerpower project:
        [dim]Run the following in your project directory:[/dim]
        [bold lightgrey]uv init --bare --no-readme[/bold lightgrey]

1. 🚀 [bold white]Create your first pipeline[/bold white]

    CLI command to create a new pipeline:

    [dim]Run the following in your project directory:[/dim]
    [bold lightgrey]flowerpower pipeline new my_first_pipeline[/bold lightgrey]

    Python API to create a new pipeline:"""
        )
        rich.print(
            rich.syntax.Syntax(
                code="""
    from flowerpower import FlowerPowerProject
    project = FlowerPowerProject.load(...)
    project.pipeline_manager.new(name="my_first_pipeline")
        """,
                lexer="python",
                theme="nord",
            )
        )

        return cls.load(
            base_dir=base_dir,
            storage_options=storage_options,
            fs=fs,
            log_level=settings.LOG_LEVEL,
        )


class FlowerPower:
    def __new__(
        self,
        name: str | None = None,
        base_dir: str | None = None,
        storage_options: dict | BaseStorageOptions | None = {},
        fs: AbstractFileSystem | None = None,
        job_queue_type: str = settings.JOB_QUEUE_TYPE,
        cfg_dir: str = settings.CONFIG_DIR,
        pipelines_dir: str = settings.PIPELINES_DIR,
        hooks_dir: str = settings.HOOKS_DIR,
    ) -> FlowerPowerProject:
        """
        Initialize a FlowerPower project.

        Args:
            name (str | None): The name of the project. If None, it defaults to the current directory name.
            base_dir (str | None): The base directory where the project will be created. If None, it defaults to the current working directory.
            storage_options (dict | BaseStorageOptions | None): Storage options for the filesystem.
            fs (AbstractFileSystem | None): An instance of AbstractFileSystem to use for file operations.
            job_queue_type (str): The type of job queue to use for the project.
            cfg_dir (str): The directory where the project configuration will be stored.
            pipelines_dir (str): The directory where the project pipelines will be stored.
            hooks_dir (str): The directory where the project hooks will be stored.

        Returns:
            FlowerPowerProject: An instance of FlowerPowerProject initialized with the new project.
        """
        if FlowerPowerProject._check_project_exists(base_dir, fs=fs):
            return FlowerPowerProject.load(
                base_dir=base_dir,
                storage_options=storage_options,
                fs=fs,
            )
        else:
            return FlowerPowerProject.init(
                name=name,
                base_dir=base_dir,
                storage_options=storage_options,
                fs=fs,
                job_queue_type=job_queue_type,
                cfg_dir=cfg_dir,
                pipelines_dir=pipelines_dir,
                hooks_dir=hooks_dir,
            )

    def __call__(self) -> FlowerPowerProject:
        """
        Call the FlowerPower instance to return the current project.

        Returns:
            FlowerPowerProject: The current FlowerPower project.
        """
        return self


def init(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict | BaseStorageOptions | None = {},
    fs: AbstractFileSystem | None = None,
    job_queue_type: str = settings.JOB_QUEUE_TYPE,
    cfg_dir: str = settings.CONFIG_DIR,
    pipelines_dir: str = settings.PIPELINES_DIR,
    hooks_dir: str = settings.HOOKS_DIR,
) -> FlowerPowerProject:
    """
    Initialize a FlowerPower project.

    Args:
        name (str | None): The name of the project. If None, it defaults to the current directory name.
        base_dir (str | None): The base directory where the project will be created. If None, it defaults to the current working directory.
        storage_options (dict | BaseStorageOptions | None): Storage options for the filesystem.
        fs (AbstractFileSystem | None): An instance of AbstractFileSystem to use for file operations.
        job_queue_type (str): The type of job queue to use for the project.
        cfg_dir (str): The directory where the project configuration will be stored.
        pipelines_dir (str): The directory where the project pipelines will be stored.
        hooks_dir (str): The directory where the project hooks will be stored.

    Returns:
        FlowerPowerProject: An instance of FlowerPowerProject initialized with the new project.
    """
    return FlowerPowerProject.init(
        name=name,
        base_dir=base_dir,
        storage_options=storage_options,
        fs=fs,
        job_queue_type=job_queue_type,
        cfg_dir=cfg_dir,
        pipelines_dir=pipelines_dir,
        hooks_dir=hooks_dir,
    )
