"""
Adapter builder for RunConfig.
"""

from typing import Any, Optional
from fsspeckit import AbstractFileSystem, BaseStorageOptions, filesystem

from ..base import BaseConfig
from .run import WithAdapterConfig


class AdapterBuilder:
    """Builder for creating WithAdapterConfig objects."""
    
    def __init__(self, adapter_config: Optional[WithAdapterConfig] = None):
        """Initialize the AdapterBuilder.
        
        Args:
            adapter_config: Initial adapter configuration to build upon.
        """
        self._config = adapter_config or WithAdapterConfig()
        self._adapter_configs = {}
    
    def enable_hamilton_tracker(self, enabled: bool = True, **kwargs) -> "AdapterBuilder":
        """Enable or disable Hamilton tracker adapter.
        
        Args:
            enabled: Whether to enable the adapter
            **kwargs: Additional configuration options
            
        Returns:
            Self for method chaining
        """
        self._config.hamilton_tracker = enabled
        if enabled and kwargs:
            self._adapter_configs['hamilton_tracker'] = kwargs
        return self
    
    def enable_mlflow(self, enabled: bool = True, **kwargs) -> "AdapterBuilder":
        """Enable or disable MLflow adapter.
        
        Args:
            enabled: Whether to enable the adapter
            **kwargs: Additional configuration options
            
        Returns:
            Self for method chaining
        """
        self._config.mlflow = enabled
        if enabled and kwargs:
            self._adapter_configs['mlflow'] = kwargs
        return self
    
    def enable_ray(self, enabled: bool = True, **kwargs) -> "AdapterBuilder":
        """Enable or disable Ray adapter.
        
        Args:
            enabled: Whether to enable the adapter
            **kwargs: Additional configuration options
            
        Returns:
            Self for method chaining
        """
        self._config.ray = enabled
        if enabled and kwargs:
            self._adapter_configs['ray'] = kwargs
        return self
    
    def enable_opentelemetry(self, enabled: bool = True, **kwargs) -> "AdapterBuilder":
        """Enable or disable OpenTelemetry adapter.
        
        Args:
            enabled: Whether to enable the adapter
            **kwargs: Additional configuration options
            
        Returns:
            Self for method chaining
        """
        self._config.opentelemetry = enabled
        if enabled and kwargs:
            self._adapter_configs['opentelemetry'] = kwargs
        return self
    
    def enable_progressbar(self, enabled: bool = True, **kwargs) -> "AdapterBuilder":
        """Enable or disable progress bar adapter.
        
        Args:
            enabled: Whether to enable the adapter
            **kwargs: Additional configuration options
            
        Returns:
            Self for method chaining
        """
        self._config.progressbar = enabled
        if enabled and kwargs:
            self._adapter_configs['progressbar'] = kwargs
        return self
    
    def enable_future(self, enabled: bool = True, **kwargs) -> "AdapterBuilder":
        """Enable or disable future adapter.
        
        Args:
            enabled: Whether to enable the adapter
            **kwargs: Additional configuration options
            
        Returns:
            Self for method chaining
        """
        self._config.future = enabled
        if enabled and kwargs:
            self._adapter_configs['future'] = kwargs
        return self
    
    def with_adapter_config(self, adapter_name: str, config: dict[str, Any]) -> "AdapterBuilder":
        """Set configuration for a specific adapter.
        
        Args:
            adapter_name: Name of the adapter
            config: Configuration dictionary
            
        Returns:
            Self for method chaining
        """
        if hasattr(self._config, adapter_name):
            self._adapter_configs[adapter_name] = config
        return self
    
    def build(self) -> WithAdapterConfig:
        """Build the final WithAdapterConfig object.
        
        Returns:
            Fully configured WithAdapterConfig object
        """
        return self._config
    
    def get_adapter_configs(self) -> dict[str, dict[str, Any]]:
        """Get the collected adapter configurations.
        
        Returns:
            Dictionary of adapter configurations
        """
        return self._adapter_configs