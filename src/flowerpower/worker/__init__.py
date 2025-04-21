from typing import Any, Optional

from ..fs import AbstractFileSystem
from .apscheduler import APSBackend, APSWorker
from .base import BaseBackend, BaseWorker
from .huey import HueyWorker
from .rq import RQBackend, RQWorker


class Worker:
    """
       Worker
    class for FlowerPower.
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
        **kwargs,
    ) -> BaseWorker:
        if type == "rq":
            return RQWorker(name, base_dir, backend, storage_options, fs, **kwargs)
        elif type == "apscheduler":
            return APSWorker(name, base_dir, backend, storage_options, fs, **kwargs)
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
