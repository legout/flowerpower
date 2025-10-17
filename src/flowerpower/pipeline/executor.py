"""Pipeline execution handling."""

from typing import TYPE_CHECKING, Any, Optional

from ..cfg.pipeline.run import RunConfig
from ..utils.config import merge_run_config_with_kwargs
from ..utils.logging import setup_logging

if TYPE_CHECKING:
    from .config_manager import PipelineConfigManager
    from .registry import PipelineRegistry


class PipelineExecutor:
    """Handles pipeline execution with comprehensive parameter handling.

    This class is responsible for:
    - Executing pipelines with various configurations
    - Merging runtime parameters with pipeline defaults
    - Setting up execution environment (logging, etc.)
    - Delegating to Pipeline objects for actual execution
    """

    def __init__(
        self,
        config_manager: "PipelineConfigManager",
        registry: "PipelineRegistry",
        project_context: Optional[Any] = None,
    ):
        """Initialize the pipeline executor.

        Args:
            config_manager: Configuration manager for accessing pipeline configs
            registry: Pipeline registry for accessing pipeline objects
            project_context: Optional project context for execution
        """
        self._config_manager = config_manager
        self._registry = registry
        self._project_context = project_context

    def run(
        self, name: str, run_config: Optional[RunConfig] = None, **kwargs
    ) -> dict[str, Any]:
        """Execute a pipeline synchronously and return its results.

        This is the main method for running pipelines directly. It handles configuration
        loading, adapter setup, and execution via Pipeline objects.

        Args:
            name: Name of the pipeline to run. Must be a valid identifier.
            run_config: Run configuration object containing all execution parameters.
                If None, the default configuration from the pipeline will be used.
            **kwargs: Additional parameters to override the run_config.

        Returns:
            dict[str, Any]: Results of pipeline execution

        Raises:
            ValueError: If pipeline configuration cannot be loaded
            Exception: If pipeline execution fails
        """
        # Load pipeline configuration
        pipeline_config = self._config_manager.load_pipeline_config(name=name)

        # Initialize run_config with pipeline defaults if not provided
        run_config = run_config or pipeline_config.run

        # Merge kwargs into run_config
        if kwargs:
            run_config = merge_run_config_with_kwargs(run_config, kwargs)

        # Set up logging for this specific run if log_level is provided
        if run_config.log_level is not None:
            setup_logging(level=run_config.log_level)

        # Get the pipeline object from registry
        pipeline = self._registry.get_pipeline(
            name=name,
            project_context=self._project_context,
        )

        # Execute the pipeline
        return pipeline.run(run_config=run_config)

    async def run_async(
        self, name: str, run_config: Optional[RunConfig] = None, **kwargs
    ) -> dict[str, Any]:
        """Execute a pipeline asynchronously and return its results.

        Args:
            name: Name of the pipeline to run
            run_config: Run configuration object
            **kwargs: Additional parameters to override the run_config

        Returns:
            dict[str, Any]: Results of pipeline execution
        """
        # Load pipeline configuration
        pipeline_config = self._config_manager.load_pipeline_config(name=name)

        # Initialize run_config with pipeline defaults if not provided
        run_config = run_config or pipeline_config.run

        # Merge kwargs into run_config
        if kwargs:
            run_config = merge_run_config_with_kwargs(run_config, kwargs)

        # Set up logging for this specific run if log_level is provided
        if run_config.log_level is not None:
            setup_logging(level=run_config.log_level)

        # Get the pipeline object from registry
        pipeline = self._registry.get_pipeline(
            name=name,
            project_context=self._project_context,
        )

        # Execute the pipeline asynchronously
        return await pipeline.run_async(run_config=run_config)
