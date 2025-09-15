"""Configuration management for pipelines."""

from typing import Optional
from fsspec_utils import AbstractFileSystem, filesystem

from ..cfg import ProjectConfig, PipelineConfig
from ..settings import CONFIG_DIR


class PipelineConfigManager:
    """Handles loading, validation, and access to pipeline configurations.
    
    This class is responsible for:
    - Loading project and pipeline configurations
    - Validating configuration files
    - Providing convenient access to configuration objects
    - Managing configuration reload logic
    """
    
    def __init__(
        self, 
        base_dir: str, 
        fs: AbstractFileSystem, 
        storage_options: dict,
        cfg_dir: str = CONFIG_DIR
    ):
        """Initialize the configuration manager.
        
        Args:
            base_dir: Base directory for the project
            fs: Filesystem instance for file operations
            storage_options: Storage options for filesystem
            cfg_dir: Configuration directory name
        """
        self._base_dir = base_dir
        self._fs = fs
        self._storage_options = storage_options
        self._cfg_dir = cfg_dir
        self._project_cfg: Optional[ProjectConfig] = None
        self._pipeline_cfg: Optional[PipelineConfig] = None
        self._current_pipeline_name: Optional[str] = None
    
    def load_project_config(self, reload: bool = False) -> ProjectConfig:
        """Load project configuration.
        
        Args:
            reload: Whether to reload the configuration even if already loaded
            
        Returns:
            ProjectConfig: The loaded project configuration
        """
        if self._project_cfg is None or reload:
            from ..cfg import ProjectConfig
            
            # Construct config file path
            cfg_path = f"{self._base_dir}/{self._cfg_dir}/project.yaml"
            
            # Load configuration
            fs = filesystem(self._base_dir, **self._storage_options)
            self._project_cfg = ProjectConfig.from_yaml(path=f"{self._cfg_dir}/project.yaml", fs=fs)
            
            # Add modules path to Python path
            self._add_modules_path(self._project_cfg.python_path)
        
        return self._project_cfg
    
    def load_pipeline_config(self, name: str, reload: bool = False) -> PipelineConfig:
        """Load pipeline configuration.
        
        Args:
            name: Name of the pipeline to load
            reload: Whether to reload the configuration even if already loaded
            
        Returns:
            PipelineConfig: The loaded pipeline configuration
        """
        if (self._pipeline_cfg is None or 
            self._current_pipeline_name != name or 
            reload):
            
            from ..cfg import PipelineConfig
            
            # Ensure project config is loaded first
            project_cfg = self.load_project_config(reload=reload)
            
            # Construct config file path
            cfg_path = f"{self._base_dir}/{self._cfg_dir}/{name}.yaml"
            
            # Load configuration
            self._pipeline_cfg = PipelineConfig.from_yaml(
                path=cfg_path,
                storage_options=self._storage_options,
                project=project_cfg,
            )
            
            # Update current pipeline name
            self._current_pipeline_name = name
        
        return self._pipeline_cfg
    
    @property
    def project_config(self) -> ProjectConfig:
        """Get the current project configuration.
        
        Returns:
            ProjectConfig: The current project configuration
            
        Raises:
            ValueError: If project configuration has not been loaded
        """
        if self._project_cfg is None:
            raise ValueError("Project configuration not loaded. Call load_project_config() first.")
        return self._project_cfg
    
    @property
    def pipeline_config(self) -> PipelineConfig:
        """Get the current pipeline configuration.
        
        Returns:
            PipelineConfig: The current pipeline configuration
            
        Raises:
            ValueError: If pipeline configuration has not been loaded
        """
        if self._pipeline_cfg is None:
            raise ValueError("Pipeline configuration not loaded. Call load_pipeline_config() first.")
        return self._pipeline_cfg
    
    @property
    def current_pipeline_name(self) -> Optional[str]:
        """Get the name of the currently loaded pipeline.
        
        Returns:
            str | None: Name of the current pipeline, or None if none loaded
        """
        return self._current_pipeline_name
    
    def _add_modules_path(self, python_path: list[str]) -> None:
        """Add module paths to Python path.
        
        Args:
            python_path: List of paths to add to sys.path
        """
        import sys
        from pathlib import Path
        
        for path in python_path:
            path_obj = Path(self._base_dir) / path
            if str(path_obj) not in sys.path:
                sys.path.insert(0, str(path_obj))