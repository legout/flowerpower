"""
Executor utilities for FlowerPower pipeline management.

This module provides factory methods for creating executor instances
with proper error handling and dependency management.
"""

from typing import Any, Dict, Optional, Union

from loguru import logger

# Lazy imports to avoid circular dependencies


class ExecutorFactory:
    """
    Factory class for creating executor instances.

    This class centralizes executor type selection and instance creation
    to reduce complexity in the Pipeline class.
    """

    def __init__(self):
        """Initialize the executor factory."""
        self._executor_cache: Dict[str, Any] = {}

    def create_executor(
        self, executor_cfg: Union[str, Dict[str, Any], Any, None]
    ) -> Any:
        """
        Create an executor instance based on configuration.

        Args:
            executor_cfg: Executor configuration (string, dict, or ExecutorConfig)

        Returns:
            Executor instance
        """
        # Normalize configuration
        executor_cfg = self._normalize_config(executor_cfg)

        # Create executor based on type
        executor_type = executor_cfg.type or "synchronous"
        cache_key = f"{executor_type}_{hash(str(executor_cfg.to_dict()))}"

        if cache_key in self._executor_cache:
            return self._executor_cache[cache_key]

        executor = self._create_executor_by_type(executor_cfg)
        self._executor_cache[cache_key] = executor
        return executor

    def _normalize_config(
        self, executor_cfg: Union[str, Dict[str, Any], Any, None]
    ) -> Any:
        """Normalize executor configuration to ExecutorConfig instance."""
        from ..cfg.pipeline.run import ExecutorConfig

        if executor_cfg is None:
            return ExecutorConfig()

        if isinstance(executor_cfg, str):
            return ExecutorConfig(type=executor_cfg)
        elif isinstance(executor_cfg, dict):
            return ExecutorConfig.from_dict(executor_cfg)
        elif not isinstance(executor_cfg, ExecutorConfig):
            raise TypeError(
                "executor_cfg must be a string, dictionary, or ExecutorConfig instance."
            )

        return executor_cfg

    def _create_executor_by_type(self, executor_cfg: Any) -> Any:
        """Create executor based on type."""
        executor_type = executor_cfg.type or "synchronous"
        if executor_type == "local":
            executor_type = "synchronous"

        if executor_type in ("synchronous", None):
            logger.debug("Using synchronous/local executor.")
            return self._create_synchronous_executor()
        elif executor_type == "threadpool":
            logger.debug("Using thread pool executor.")
            return self._create_threadpool_executor(executor_cfg)
        elif executor_type == "processpool":
            logger.debug("Using process pool executor.")
            return self._create_processpool_executor(executor_cfg)
        elif executor_type == "ray":
            logger.debug("Using Ray executor.")
            return self._create_ray_executor(executor_cfg)
        elif executor_type == "dask":
            logger.debug("Using Dask executor.")
            return self._create_dask_executor(executor_cfg)
        else:
            logger.warning(
                f"Unknown executor type: {executor_type}. Using local executor."
            )
            return self._create_synchronous_executor()

    def _create_synchronous_executor(self) -> Any:
        """Create synchronous/local executor."""
        from hamilton.execution.executors import SynchronousLocalTaskExecutor

        return SynchronousLocalTaskExecutor()

    def _create_threadpool_executor(self, executor_cfg: Any) -> Any:
        """Create thread pool executor."""
        try:
            from hamilton.execution.executors import MultiThreadingExecutor

            # Extract max workers from config
            if executor_cfg.max_workers is not None:
                return MultiThreadingExecutor(max_tasks=executor_cfg.max_workers)
            return MultiThreadingExecutor()
        except ImportError:
            logger.warning(
                "ThreadPool executor dependencies not installed. Using local executor."
            )
            return self._create_synchronous_executor()

    def _create_processpool_executor(self, executor_cfg: Any) -> Any:
        """Create process pool executor."""
        try:
            from hamilton.execution.executors import MultiProcessingExecutor

            # Extract max workers from config
            if executor_cfg.max_workers is not None:
                return MultiProcessingExecutor(max_tasks=executor_cfg.max_workers)
            return MultiProcessingExecutor()
        except ImportError:
            logger.warning(
                "ProcessPool executor dependencies not installed. Using local executor."
            )
            return self._create_synchronous_executor()

    def _create_ray_executor(self, executor_cfg: Any) -> Any:
        """Create Ray executor."""
        try:
            from hamilton.plugins.h_ray import RayTaskExecutor

            # Extract configuration
            config = {}
            if executor_cfg.num_cpus is not None:
                config["num_cpus"] = executor_cfg.num_cpus
            if config:
                return RayTaskExecutor(**config)
            return RayTaskExecutor()
        except ImportError:
            logger.warning(
                "Ray executor dependencies not installed. Using local executor."
            )
            return self._create_synchronous_executor()

    def _create_dask_executor(self, executor_cfg: Any) -> Any:
        """Create Dask executor."""
        try:
            from hamilton.plugins.h_dask import DaskExecutor

            # Extract configuration
            config = {}
            if executor_cfg.num_cpus is not None:
                config["num_cpus"] = executor_cfg.num_cpus
            if config:
                return DaskExecutor(**config)
            return DaskExecutor()
        except ImportError:
            logger.warning(
                "Dask executor dependencies not installed. Using local executor."
            )
            return self._create_synchronous_executor()

    def clear_cache(self) -> None:
        """Clear the executor cache."""
        self._executor_cache.clear()


def create_executor_factory() -> ExecutorFactory:
    """
    Factory function to create an ExecutorFactory instance.

    Returns:
        ExecutorFactory: Configured factory instance
    """
    return ExecutorFactory()
