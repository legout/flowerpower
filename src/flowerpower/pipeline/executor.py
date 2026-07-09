"""Pipeline execution handling."""

from typing import TYPE_CHECKING, Any

from ..cfg.pipeline.run import RunConfig
from ..utils.config import (
    merge_run_config_with_kwargs,
    merge_run_configs,
    validate_resolved_run_config,
)
from ..utils.logging import setup_logging
from .execution_context import resolve_run_config_adapter_configs

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
        project_context: Any | None = None,
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

    @classmethod
    def from_context(
        cls,
        context,
        *,
        config_manager: "PipelineConfigManager",
        registry: "PipelineRegistry",
    ) -> "PipelineExecutor":
        """Create an executor bound to project runtime context."""
        return cls(
            config_manager=config_manager,
            registry=registry,
            project_context=context,
        )

    def run(self, name: str, run_config: RunConfig | None = None, **kwargs) -> dict[str, Any]:
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

        # Load pipeline configuration (ConfigManager is stateless — always fresh)
        pipeline_config = self._config_manager.load_pipeline_config(name)

        # Merge runtime overrides onto a copy of pipeline defaults.
        run_config = self._merge_pipeline_run_config(pipeline_config.run, run_config)

        # Merge kwargs into run_config
        if kwargs:
            run_config = merge_run_config_with_kwargs(run_config, kwargs)

        # Fold pipeline and project adapter defaults into the resolved RunConfig
        # so runtime object construction consumes the resolved values only.
        run_config = resolve_run_config_adapter_configs(
            run_config, pipeline_config, self._project_adapter_base()
        )

        # Guard against non-clearable fields that were left unset.
        validate_resolved_run_config(run_config)

        # Set up logging for this specific run if log_level is provided
        if run_config.log_level is not None:
            setup_logging(level=run_config.log_level)

        # Get the pipeline object from registry
        pipeline = self._registry.get_pipeline(
            name=name,
            project_context=self._project_context,
            reload=run_config.reload,
        )

        # Execute the pipeline through the resolved-only seam so the public
        # Pipeline.run path is not re-entered after the config is resolved here.
        return pipeline._run_resolved(run_config=run_config)

    async def run_async(
        self, name: str, run_config: RunConfig | None = None, **kwargs
    ) -> dict[str, Any]:
        """Execute a pipeline asynchronously and return its results using Hamilton's async driver.

        Args:
            name: Name of the pipeline to run.
            run_config: Run configuration object. When ``async_driver`` is ``None`` or ``True``
                the Hamilton async driver is used; setting it to ``False`` raises a
                ``ValueError``.
            **kwargs: Additional parameters to override the run_config.

        Returns:
            dict[str, Any]: Results of pipeline execution.
        """

        # Load pipeline configuration (ConfigManager is stateless — always fresh)
        pipeline_config = self._config_manager.load_pipeline_config(name)

        # Merge runtime overrides onto a copy of pipeline defaults.
        run_config = self._merge_pipeline_run_config(pipeline_config.run, run_config)

        # Merge kwargs into run_config
        if kwargs:
            run_config = merge_run_config_with_kwargs(run_config, kwargs)

        # Fold pipeline and project adapter defaults into the resolved RunConfig
        # so runtime object construction consumes the resolved values only.
        run_config = resolve_run_config_adapter_configs(
            run_config, pipeline_config, self._project_adapter_base()
        )

        # Guard against non-clearable fields that were left unset.
        validate_resolved_run_config(run_config)

        # Set up logging for this specific run if log_level is provided
        if run_config.log_level is not None:
            setup_logging(level=run_config.log_level)

        # Get the pipeline object from registry
        pipeline = self._registry.get_pipeline(
            name=name,
            project_context=self._project_context,
            reload=run_config.reload,
        )

        # Execute the pipeline asynchronously
        return await pipeline.run_async(run_config=run_config)

    def _project_adapter_base(self) -> Any:
        """Return project adapter defaults from the registry-owned project config."""
        project_cfg = getattr(self._registry, "project_cfg", None)
        return getattr(project_cfg, "adapter", None) if project_cfg is not None else None

    @staticmethod
    def _merge_pipeline_run_config(
        base: RunConfig,
        override: RunConfig | None,
    ) -> RunConfig:
        """Merge runtime overrides onto a defensive copy of pipeline defaults."""
        return merge_run_configs(base, override)
