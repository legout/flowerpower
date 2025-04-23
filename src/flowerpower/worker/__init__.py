from typing import Any, Optional

from ..fs import AbstractFileSystem
from ..utils.logging import setup_logging
from .apscheduler import APSBackend, APSWorker
from .base import BaseBackend, BaseWorker
from .huey import HueyWorker
from .rq import RQBackend, RQWorker

setup_logging()


class Worker:
    """
    Worker class for FlowerPower.
    This class serves as a factory for creating worker instances based on the specified backend type.
    """

    def __new__(
        cls,
        type: str = "rq",
        name: str | None = None,
        base_dir: str | None = None,
        backend: BaseBackend | None = None,
        storage_options: Optional[dict[str, Any]] = None,
        fs: AbstractFileSystem | None = None,
        log_level: str | None = None,
        **kwargs,
    ) -> BaseWorker:
        """
        Create a new worker instance based on the specified backend type.

        Args:
            type (str): The type of worker to create. Valid types are 'rq', 'apscheduler', and 'huey'.
            name (str | None): The name of the worker.
            base_dir (str | None): The base directory for the worker.
            backend (BaseBackend | None): The backend instance to use.
            storage_options (dict[str, Any] | None): Storage options for the worker.
            fs (AbstractFileSystem | None): File system instance to use.
            log_level (str | None): Logging level for the worker.
            **kwargs: Additional keyword arguments for the worker.

        Returns:
            BaseWorker: An instance of the specified worker type.
        """
        if type == "rq":
            return RQWorker(
                name=name,
                base_dir=base_dir,
                backend=backend,
                storage_options=storage_options,
                fs=fs,
                log_level=log_level,
                **kwargs,
            )
        elif type == "apscheduler":
            return APSWorker(
                name=name,
                base_dir=base_dir,
                backend=backend,
                storage_options=storage_options,
                fs=fs,
                log_level=log_level,
                **kwargs,
            )
        elif type == "huey":
            return HueyWorker(name, base_dir, backend, storage_options, fs, **kwargs)
        else:
            raise ValueError(
                f"Invalid backend type: {type}. Valid types: ['rq', 'apscheduler', 'huey']"
            )


class Backend:
    """
    Backend class for FlowerPower.
    This class serves as a factory for creating backend instances based on the specified backend type.
    """

    def __new__(
        cls,
        worker_type: str,
        **kwargs,
    ) -> BaseBackend:
        if worker_type == "rq":
            return RQBackend(**kwargs)
        elif worker_type == "apscheduler":
            return APSBackend(**kwargs)
        else:
            raise ValueError(
                f"Invalid backend type: {worker_type}. Valid types: ['rq', 'apscheduler']"
            )


__all__ = [
    "Worker",
    "RQWorker",
    "APSWorker",
    "HueyWorker",
    "Backend",
    "RQBackend",
    "APSBackend",
]
