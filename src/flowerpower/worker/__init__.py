from .apscheduler import APSWorker, APSBackend
from .rq import RQWorker, RQBackend
from .huey import HueyWorker
from .base import BaseBackend, BaseWorker
from typing import Any, Optional
from ..fs import AbstractFileSystem


class Worker:
    """
    Worker class for FlowerPower.
    This class serves as a factory for creating worker instances based on the specified backend type.
    """

    def __new__(
        cls,
        backend_type: str="rq",
        name: str | None = None,
        base_dir: str | None = None,
        backend: BaseBackend | None = None,
        storage_options: Optional[dict[str, Any]] = None,
        fs: AbstractFileSystem | None = None,
        **kwargs,
    )->BaseWorker:

        if backend_type == "rq":
            return RQWorker(name, base_dir, backend, storage_options, fs, **kwargs)
        elif backend_type == "apscheduler":
            return APSWorker(name, base_dir, backend, storage_options, fs, **kwargs)
        elif backend_type == "huey":
            return HueyWorker(name, base_dir, backend, storage_options, fs, **kwargs)
        else:
            raise ValueError(
                f"Invalid backend type: {backend_type}. Valid types: ['rq', 'apscheduler', 'huey']"
            )


class Backend:
    """
    Backend class for FlowerPower.
    This class serves as a factory for creating backend instances based on the specified backend type.
    """

    def __new__(
        cls,
        backend_type: str,
        **kwargs,
    )->BaseBackend:
        if backend_type == "rq":
            return RQBackend(**kwargs)
        elif backend_type == "apscheduler":
            return APSBackend(**kwargs)
        else:
            raise ValueError(
                f"Invalid backend type: {backend_type}. Valid types: ['rq', 'apscheduler']"
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