"""Configuration management for pipelines."""

import os
from typing import TYPE_CHECKING, Optional

from fsspeckit import AbstractFileSystem

from ..cfg import PipelineConfig, ProjectConfig
from ..settings import CONFIG_DIR
from ..utils.misc import get_filesystem
from ..utils.env import (
    parse_env_overrides,
    build_specific_overlays,
    apply_global_shims,
)

if TYPE_CHECKING:
    from fsspeckit import AbstractFileSystem


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
        self._fs = fs
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
            cfg_path = f"{self._base_dir}/{self._cfg_dir}/project.yml"
            
            # Load configuration using provided filesystem
            fs = self._fs
            self._project_cfg = ProjectConfig.from_yaml(path=f"{self._cfg_dir}/project.yml", fs=fs)

            # Apply environment overlays (project-only part)
            try:
                overrides = parse_env_overrides()
                proj_overlay, pipe_overlay = build_specific_overlays(overrides)
                apply_global_shims(overrides, proj_overlay, pipe_overlay)
                if proj_overlay.get("project") and hasattr(self._project_cfg, "update"):
                    self._project_cfg.update(proj_overlay["project"])  
            except Exception:
                pass
            
            # Add pipelines directory to Python path
            self._add_modules_path(["pipelines"])
        
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
            self.load_project_config(reload=reload)

            # Use existing filesystem
            fs = self._fs

            # Try different file locations and extensions
            cfg_path = None
            possible_paths = [
                # Try .yml extension in pipelines/ subdirectory first
                os.path.join(self._cfg_dir, "pipelines", f"{name}.yml"),
                # Then try .yaml extension in pipelines/ subdirectory
                os.path.join(self._cfg_dir, "pipelines", f"{name}.yaml"),
                # Fallback to old paths for backward compatibility
                os.path.join(self._cfg_dir, f"{name}.yml"),
                os.path.join(self._cfg_dir, f"{name}.yaml"),
            ]

            for path in possible_paths:
                try:
                    if fs.exists(path):
                        cfg_path = path
                        break
                except Exception:
                    continue

            if cfg_path is None:
                raise FileNotFoundError(
                    f"Pipeline configuration not found. Searched for: {possible_paths}"
                )

            # Load configuration
            self._pipeline_cfg = PipelineConfig.from_yaml(
                name=name,
                path=cfg_path,
                fs=fs,
            )

            # Apply environment overlays (pipeline-only part)
            try:
                overrides = parse_env_overrides()
                proj_overlay, pipe_overlay = build_specific_overlays(overrides)
                apply_global_shims(overrides, proj_overlay, pipe_overlay)
                if pipe_overlay.get("pipeline") and hasattr(self._pipeline_cfg, "update"):
                    self._pipeline_cfg.update(pipe_overlay["pipeline"])  
            except Exception:
                pass

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