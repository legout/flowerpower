"""JobQueueManagerFactory for FlowerPower job queue managers."""

from typing import Any, Optional

from ..fs import AbstractFileSystem
from .rq.manager import RQBackend, RQManager


class JobQueueManagerFactory:
    """Factory for creating job queue manager instances."""

    @staticmethod
    def get_manager(
        manager_type: str = "rq",
        *,
        name: str = "rq_scheduler",
        base_dir: Optional[str] = None,
        backend: Optional[RQBackend] = None,
        storage_options: Optional[dict[str, Any]] = None,
        fs: Optional[AbstractFileSystem] = None,
        log_level: Optional[str] = None,
        **kwargs,
    ):
        """
        Return an instance of the appropriate job queue manager.

        Args:
            manager_type: The type of job queue manager to create. Only 'rq' is supported.
            name: Name for the manager instance.
            base_dir: Project base directory.
            backend: RQBackend instance for Redis connection.
            storage_options: Storage options for file system.
            fs: Custom filesystem implementation.
            log_level: Logging level.
            kwargs: Additional arguments (ignored).

        Returns:
            Instance of a job queue manager.

        Raises:
            ValueError: If an unsupported manager_type is given.
        """
        if manager_type == "rq":
            return RQManager(
                name=name,
                base_dir=base_dir,
                backend=backend,
                storage_options=storage_options,
                fs=fs,
                log_level=log_level,
            )
        raise ValueError(f"Unsupported manager_type: {manager_type}")
