import copy
from typing import Any, Callable, Optional, Union

from fsspec_utils import AbstractFileSystem, BaseStorageOptions, filesystem

from ... import settings
from ..base import BaseConfig
from .adapter import AdapterConfig as PipelineAdapterConfig
from .run import ExecutorConfig, RunConfig, WithAdapterConfig
from ..project.adapter import AdapterConfig as ProjectAdapterConfig


class RunConfigBuilder:
    """A fluent builder for creating RunConfig objects.
    
    This builder provides a clean interface for constructing RunConfig objects
    with proper configuration merging from project and pipeline defaults.
    """
    
    def __init__(
        self, 
        pipeline_name: str, 
        base_dir: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions | None = {}
    ):
        """Initialize the RunConfigBuilder.
        
        Args:
            pipeline_name: Name of the pipeline to build config for
            base_dir: Base directory for the project (defaults to current directory)
            fs: Optional filesystem instance
            storage_options: Options for filesystem access
        """
        self.pipeline_name = pipeline_name
        self.base_dir = base_dir or "."
        self._fs = fs
        self._storage_options = storage_options
        
        # Initialize with empty config
        self._config = RunConfig()
        
        # Load defaults from pipeline and project configs
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default configuration from pipeline and project YAML files."""
        if self._fs is None:
            self._fs = filesystem(
                self.base_dir, 
                cached=False, 
                dirfs=True, 
                storage_options=self._storage_options
            )
        
        # Load pipeline configuration
        try:
            from .. import PipelineConfig
            pipeline_cfg = PipelineConfig.load(
                base_dir=self.base_dir,
                name=self.pipeline_name,
                fs=self._fs,
                storage_options=self._storage_options
            )
            if pipeline_cfg and pipeline_cfg.run:
                self._config = copy.deepcopy(pipeline_cfg.run)
        except Exception:
            # If pipeline config doesn't exist, use defaults
            pass
        
        # Load project configuration for adapter defaults
        try:
            from .. import ProjectConfig
            project_cfg = ProjectConfig.load(
                base_dir=self.base_dir,
                fs=self._fs,
                storage_options=self._storage_options
            )
            if project_cfg and project_cfg.adapter:
                # Store project adapter config for merging
                self._project_adapter_cfg = project_cfg.adapter
            else:
                self._project_adapter_cfg = ProjectAdapterConfig()
        except Exception:
            self._project_adapter_cfg = ProjectAdapterConfig()
    
    def with_inputs(self, inputs: dict) -> "RunConfigBuilder":
        """Set pipeline input values.
        
        Args:
            inputs: Dictionary of input values to override defaults
            
        Returns:
            Self for method chaining
        """
        if inputs:
            if self._config.inputs is None:
                self._config.inputs = {}
            self._config.inputs.update(inputs)
        return self
    
    def with_final_vars(self, final_vars: list[str]) -> "RunConfigBuilder":
        """Set the final output variables.
        
        Args:
            final_vars: List of variable names to return from execution
            
        Returns:
            Self for method chaining
        """
        self._config.final_vars = final_vars
        return self
    
    def with_config(self, config: dict) -> "RunConfigBuilder":
        """Set Hamilton driver configuration.
        
        Args:
            config: Dictionary of configuration values for Hamilton
            
        Returns:
            Self for method chaining
        """
        if config:
            if self._config.config is None:
                self._config.config = {}
            self._config.config.update(config)
        return self
    
    def with_cache(self, cache: Union[dict, bool]) -> "RunConfigBuilder":
        """Set cache configuration.
        
        Args:
            cache: Cache configuration (dict) or enable/disable flag (bool)
            
        Returns:
            Self for method chaining
        """
        self._config.cache = cache
        return self
    
    def with_executor(self, executor_type: str, **kwargs) -> "RunConfigBuilder":
        """Set executor configuration.
        
        Args:
            executor_type: Type of executor ('synchronous', 'threadpool', 'processpool', 'ray', 'dask')
            **kwargs: Additional executor configuration options
            
        Returns:
            Self for method chaining
        """
        if not self._config.executor:
            self._config.executor = ExecutorConfig()
        
        self._config.executor.type = executor_type
        
        # Apply additional executor options
        for key, value in kwargs.items():
            if hasattr(self._config.executor, key):
                setattr(self._config.executor, key, value)
        
        return self
    
    def with_adapter(self, adapter_name: str, **kwargs) -> "RunConfigBuilder":
        """Enable and configure a specific adapter.
        
        Args:
            adapter_name: Name of the adapter ('hamilton_tracker', 'mlflow', 'opentelemetry', etc.)
            **kwargs: Adapter-specific configuration options
            
        Returns:
            Self for method chaining
        """
        if not self._config.with_adapter:
            self._config.with_adapter = WithAdapterConfig()
        
        # Enable the adapter
        if hasattr(self._config.with_adapter, adapter_name):
            setattr(self._config.with_adapter, adapter_name, True)
            
            # Store adapter configuration for merging
            if not hasattr(self, '_adapter_configs'):
                self._adapter_configs = {}
            self._adapter_configs[adapter_name] = kwargs
        
        return self
    
    def with_retries(
        self, 
        max_attempts: int = 3, 
        delay: float = 1.0, 
        jitter: float = 0.1,
        exceptions: Optional[list] = None
    ) -> "RunConfigBuilder":
        """Configure retry behavior.
        
        Args:
            max_attempts: Maximum number of retry attempts
            delay: Base delay between retries in seconds
            jitter: Random jitter factor to add to retry delay
            exceptions: List of exception types that should trigger retries
            
        Returns:
            Self for method chaining
        """
        self._config.max_retries = max_attempts
        self._config.retry_delay = delay
        self._config.jitter_factor = jitter
        
        if exceptions:
            self._config.retry_exceptions = exceptions
        
        return self
    
    def with_callbacks(
        self, 
        on_success: Optional[Callable] = None, 
        on_failure: Optional[Callable] = None
    ) -> "RunConfigBuilder":
        """Set success and failure callbacks.
        
        Args:
            on_success: Callback function to execute on successful completion
            on_failure: Callback function to execute on failure
            
        Returns:
            Self for method chaining
        """
        if on_success:
            self._config.on_success = on_success
        if on_failure:
            self._config.on_failure = on_failure
        
        return self
    
    def with_log_level(self, log_level: str) -> "RunConfigBuilder":
        """Set the log level for execution.
        
        Args:
            log_level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
            
        Returns:
            Self for method chaining
        """
        self._config.log_level = log_level
        return self
    
    def with_reload(self, reload: bool = True) -> "RunConfigBuilder":
        """Set whether to reload the pipeline module.
        
        Args:
            reload: Whether to force reload of the pipeline module
            
        Returns:
            Self for method chaining
        """
        self._config.reload = reload
        return self
    
    def with_pipeline_adapter_config(self, config: dict) -> "RunConfigBuilder":
        """Set pipeline-specific adapter configuration.
        
        Args:
            config: Pipeline adapter configuration dictionary
            
        Returns:
            Self for method chaining
        """
        if config:
            if self._config.pipeline_adapter_cfg is None:
                self._config.pipeline_adapter_cfg = {}
            self._config.pipeline_adapter_cfg.update(config)
        return self
    
    def with_project_adapter_config(self, config: dict) -> "RunConfigBuilder":
        """Set project-level adapter configuration.
        
        Args:
            config: Project adapter configuration dictionary
            
        Returns:
            Self for method chaining
        """
        if config:
            if self._config.project_adapter_cfg is None:
                self._config.project_adapter_cfg = {}
            self._config.project_adapter_cfg.update(config)
        return self
    
    def with_custom_adapter(self, name: str, adapter: Any) -> "RunConfigBuilder":
        """Add a custom adapter instance.
        
        Args:
            name: Name/identifier for the adapter
            adapter: Adapter instance
            
        Returns:
            Self for method chaining
        """
        if self._config.adapter is None:
            self._config.adapter = {}
        self._config.adapter[name] = adapter
        return self
    
    def build(self) -> RunConfig:
        """Build the final RunConfig object.
        
        This method merges all configurations and validates the final result.
        
        Returns:
            Fully configured RunConfig object
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Create a deep copy to avoid modifying the internal state
        final_config = copy.deepcopy(self._config)
        
        # Merge adapter configurations
        if hasattr(self, '_adapter_configs') and self._adapter_configs:
            self._merge_adapter_configs(final_config)
        
        # Validate configuration
        self._validate_config(final_config)
        
        return final_config
    
    def _merge_adapter_configs(self, config: RunConfig):
        """Merge adapter configurations from builder with project/pipeline configs."""
        if not config.pipeline_adapter_cfg:
            config.pipeline_adapter_cfg = {}
        
        if not config.project_adapter_cfg:
            config.project_adapter_cfg = {}
        
        # Merge project adapter defaults
        for adapter_name, adapter_config in self._adapter_configs.items():
            if adapter_name in ['hamilton_tracker', 'mlflow', 'opentelemetry']:
                # Merge with project config
                if hasattr(self._project_adapter_cfg, adapter_name):
                    project_config = getattr(self._project_adapter_cfg, adapter_name).to_dict()
                    adapter_config = {**project_config, **adapter_config}
                
                # Store in pipeline adapter config
                if adapter_name not in config.pipeline_adapter_cfg:
                    config.pipeline_adapter_cfg[adapter_name] = {}
                config.pipeline_adapter_cfg[adapter_name].update(adapter_config)
    
    def _validate_config(self, config: RunConfig):
        """Validate the final configuration.
        
        Args:
            config: RunConfig object to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate retry configuration
        if config.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        
        if config.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")
        
        if config.jitter_factor is not None and config.jitter_factor < 0:
            raise ValueError("jitter_factor must be non-negative")
        
        # Validate executor configuration
        if config.executor and config.executor.type:
            valid_executors = ['synchronous', 'threadpool', 'processpool', 'ray', 'dask']
            if config.executor.type not in valid_executors:
                raise ValueError(f"Invalid executor type: {config.executor.type}")
        
        # Validate log level
        if config.log_level:
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if config.log_level.upper() not in valid_levels:
                raise ValueError(f"Invalid log level: {config.log_level}")