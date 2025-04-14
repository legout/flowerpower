from .apscheduler import APSWorker
from .rq import RQWorker
from .base import BaseBackend
from typing import Any
from ..fs import AbstractFileSystem


class Worker:
    """
    Worker class for FlowerPower.
    This class serves as a factory for creating worker instances based on the specified backend type.
    """

    def __new__(
        cls,
        name: str | None = None,
        base_dir: str | None = None,
        backend: BaseBackend | None = None,
        storage_options: dict[str, Any] = None,
        fs: AbstractFileSystem | None = None,
        **kwargs,
    ):
        backend_type = kwargs.get("backend_type", None)
        if backend_type == "rq":
            return RQWorker(name, base_dir, backend, storage_options, fs, **kwargs)
        elif backend_type == "apscheduler":
            return APSWorker(name, base_dir, backend, storage_options, fs, **kwargs)
        else:
            raise ValueError(
                f"Invalid backend type: {backend_type}. Valid types: ['rq', 'apscheduler']"
            )
