"""
Executor builder for RunConfig.
"""

from typing import Any, Optional, Union
from fsspeckit import AbstractFileSystem, BaseStorageOptions, filesystem

from ... import settings
from ..base import BaseConfig
from .run import ExecutorConfig


class ExecutorBuilder:
    """Builder for creating ExecutorConfig objects."""

    def __init__(self, executor_config: Optional[ExecutorConfig] = None):
        """Initialize the ExecutorBuilder.

        Args:
            executor_config: Initial executor configuration to build upon.
        """
        self._config = executor_config or ExecutorConfig()

    def with_type(self, executor_type: str) -> "ExecutorBuilder":
        """Set the executor type.

        Args:
            executor_type: Type of executor ('synchronous', 'threadpool', 'processpool', 'ray', 'dask')

        Returns:
            Self for method chaining
        """
        self._config.type = executor_type
        return self

    def with_max_workers(self, max_workers: int) -> "ExecutorBuilder":
        """Set the maximum number of workers.

        Args:
            max_workers: Maximum number of worker threads/processes

        Returns:
            Self for method chaining
        """
        self._config.max_workers = max_workers
        return self

    def with_num_cpus(self, num_cpus: int) -> "ExecutorBuilder":
        """Set the number of CPUs to use.

        Args:
            num_cpus: Number of CPUs to allocate

        Returns:
            Self for method chaining
        """
        self._config.num_cpus = num_cpus
        return self

    def with_config(self, config: dict[str, Any]) -> "ExecutorBuilder":
        """Apply additional configuration options.

        Args:
            config: Dictionary of additional configuration options

        Returns:
            Self for method chaining
        """
        for key, value in config.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        return self

    def build(self) -> ExecutorConfig:
        """Build the final ExecutorConfig object.

        Returns:
            Fully configured ExecutorConfig object

        Raises:
            ValueError: If configuration is invalid
        """
        self._validate_config()
        return self._config

    def _validate_config(self) -> None:
        """Validate the executor configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if self._config.type:
            valid_executors = [
                "synchronous",
                "threadpool",
                "processpool",
                "ray",
                "dask",
            ]
            if self._config.type not in valid_executors:
                raise ValueError(f"Invalid executor type: {self._config.type}")

        if self._config.max_workers is not None and self._config.max_workers < 1:
            raise ValueError("max_workers must be at least 1")

        if self._config.num_cpus is not None and self._config.num_cpus < 1:
            raise ValueError("num_cpus must be at least 1")
