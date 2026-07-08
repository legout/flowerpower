"""Pipeline catalog for discovery and listing of pipeline modules."""

from __future__ import annotations

import posixpath
from typing import Any, Callable

import yaml
from fsspeckit import AbstractFileSystem
from loguru import logger

from ..cfg import PipelineConfig, ProjectConfig
from ..utils.filesystem import format_pipeline_file_path, get_pipeline_config_paths
from ..utils.security import SecurityError, validate_pipeline_name


class PipelineCatalog:
    """Discovers, lists, and summarizes pipeline modules.

    This class is responsible for the presentation-free side of pipeline
    discovery: scanning the pipelines directory, resolving canonical names from
    stored configuration, and gathering metadata/summaries.  It delegates
    configuration loading to callables so it stays independent of the loader.

    Attributes:
        _fs: Filesystem instance used for directory scanning and file reads.
        _cfg_dir: Configuration directory name.
        _pipelines_dir: Pipelines directory name.
        _project_cfg: Static project configuration fallback.
        _config_provider: Callable that returns a ``PipelineConfig`` for a name.
        _project_cfg_provider: Callable that returns the current ``ProjectConfig``.
    """

    def __init__(
        self,
        fs: AbstractFileSystem,
        cfg_dir: str,
        pipelines_dir: str,
        project_cfg: ProjectConfig | None = None,
        *,
        config_provider: Callable[[str], PipelineConfig] | None = None,
        project_cfg_provider: Callable[[], ProjectConfig | None] | None = None,
    ) -> None:
        """Initialize the PipelineCatalog.

        Args:
            fs: Filesystem instance.
            cfg_dir: Configuration directory name.
            pipelines_dir: Pipelines directory name.
            project_cfg: Optional static project configuration fallback.
            config_provider: Optional callable ``name -> PipelineConfig`` used when
                a summary requests configuration data.
            project_cfg_provider: Optional callable returning the current project
                configuration.  When set, it takes precedence over ``project_cfg``.
        """
        self._fs = fs
        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir
        self._project_cfg = project_cfg
        self._config_provider = config_provider
        self._project_cfg_provider = project_cfg_provider

    # --- Pipeline Discovery & Listing ---

    def get_files(self) -> list[str]:
        """
        Get the list of pipeline files.

        Returns:
            list[str]: The list of pipeline files.
        """
        try:
            files: list[str] = []
            seen: set[str] = set()
            discovery_error_logged = False
            patterns = (
                posixpath.join(self._pipelines_dir, "*.py"),
                posixpath.join(self._pipelines_dir, "**", "*.py"),
            )
            for pattern in patterns:
                try:
                    paths = self._fs.glob(pattern)
                except NotImplementedError as e:
                    logger.debug(
                        f"Skipping unsupported pipeline glob pattern {pattern}: {e}"
                    )
                    continue
                except Exception as e:
                    if not discovery_error_logged:
                        logger.error(
                            f"Error accessing pipeline glob pattern {pattern}: {e}"
                        )
                        discovery_error_logged = True
                    continue

                for path in paths:
                    if posixpath.basename(path) == "__init__.py" or path in seen:
                        continue
                    seen.add(path)
                    files.append(path)
            return sorted(files)
        except (OSError, PermissionError) as e:
            logger.error(
                f"Error accessing pipeline directory {self._pipelines_dir}: {e}"
            )
            return []
        except Exception as e:
            logger.error(
                f"Unexpected error accessing pipeline directory {self._pipelines_dir}: {e}"
            )
            return []

    def get_names(self) -> list[str]:
        """
        Get the list of pipeline names.

        Returns:
            list[str]: The list of pipeline names.
        """
        return [self.path_to_pipeline_name(path) for path in self.get_files()]

    def path_to_pipeline_name(self, path: str) -> str:
        """Convert a pipeline file path into a discovered pipeline name."""
        relative_path = posixpath.relpath(path, self._pipelines_dir)
        module_path = posixpath.splitext(relative_path)[0]
        derived_name = module_path.replace("/", ".")
        stored_name = self.read_stored_pipeline_name(module_path)
        return stored_name or derived_name

    def read_stored_pipeline_name(self, module_path: str) -> str | None:
        """Return the canonical pipeline name from YAML when available."""
        candidate_paths = get_pipeline_config_paths(
            module_path,
            self._cfg_dir,
            self._pipelines_dir,
        )

        for cfg_path in candidate_paths:
            try:
                exists = self._fs.exists(cfg_path)
            except Exception as error:
                logger.debug(
                    f"Skipping unreadable pipeline config candidate {cfg_path}: {error}"
                )
                continue

            if not exists:
                continue
            try:
                with self._fs.open(cfg_path) as f:
                    data = yaml.safe_load(f) or {}
            except Exception as e:
                logger.debug(
                    f"Skipping unreadable pipeline config candidate {cfg_path}: {e}"
                )
                continue

            stored_name = data.get("name") if isinstance(data, dict) else None
            if isinstance(stored_name, str) and stored_name:
                try:
                    return validate_pipeline_name(stored_name)
                except (SecurityError, ValueError):
                    continue

        return None

    # --- Data Gathering (presentation-free) ---

    def get_summary(
        self,
        name: str | None = None,
        cfg: bool = True,
        code: bool = True,
        project: bool = True,
    ) -> dict[str, Any]:
        """
        Get a summary of the pipelines.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None.
            cfg (bool, optional): Whether to show the configuration. Defaults to True.
            code (bool, optional): Whether to show the module. Defaults to True.
            project (bool, optional): Whether to show the project configuration. Defaults to True.
        Returns:
            dict[str, dict | str]: A dictionary containing the pipeline summary.

        Examples:
            ```python
            pm = PipelineManager()
            summary=pm.get_summary()
            ```
        """
        if name is not None:
            name = validate_pipeline_name(name)
            pipeline_names = [name]
        else:
            pipeline_names = self.get_names()

        summary: dict[str, Any] = {}
        summary["pipelines"] = {}

        if project:
            project_cfg = (
                self._project_cfg_provider()
                if self._project_cfg_provider is not None
                else self._project_cfg
            )
            if project_cfg is not None:
                summary["project"] = project_cfg.to_dict()

        for name in pipeline_names:
            # Load pipeline config directly

            pipeline_summary = {}
            if cfg:
                if self._config_provider is None:
                    raise RuntimeError(
                        "PipelineCatalog requires config_provider to load configuration summaries"
                    )
                pipeline_cfg = self._config_provider(name)
                pipeline_summary["cfg"] = pipeline_cfg.to_dict()
            if code:
                try:
                    module_path = posixpath.join(
                        self._pipelines_dir,
                        f"{format_pipeline_file_path(name)}.py",
                    )
                    module_content = self._fs.cat(module_path).decode()
                    pipeline_summary["module"] = module_content
                except FileNotFoundError:
                    logger.warning(f"Module file not found for pipeline '{name}'")
                    pipeline_summary["module"] = "# Module file not found"
                except (OSError, PermissionError, UnicodeDecodeError) as e:
                    logger.error(
                        f"Error reading module file for pipeline '{name}': {e}"
                    )
                    pipeline_summary["module"] = f"# Error reading module file: {e}"
                except Exception as e:
                    logger.error(
                        f"Unexpected error reading module file for pipeline '{name}': {e}"
                    )
                    pipeline_summary["module"] = (
                        f"# Unexpected error reading module file: {e}"
                    )

            if pipeline_summary:  # Only add if cfg or code was requested and found
                summary["pipelines"][name] = pipeline_summary
        return summary

    def collect_pipeline_info(self) -> list[dict[str, Any]]:
        """Collect metadata (name, path, mod_time, size) for all pipelines.

        Returns:
            A list of dicts, each with keys ``name``, ``path``, ``mod_time``,
            and ``size``.  Returns an empty list when no pipelines exist.
        """
        pipeline_files = self.get_files()
        pipeline_names = [self.path_to_pipeline_name(path) for path in pipeline_files]

        if not pipeline_files:
            return []

        pipeline_info: list[dict[str, Any]] = []

        for path, name in zip(pipeline_files, pipeline_names, strict=True):
            try:
                mod_time = self._fs.modified(path).strftime("%Y-%m-%d %H:%M:%S")
            except NotImplementedError:
                mod_time = "N/A"
            try:
                size_bytes = self._fs.size(path)
                size = f"{size_bytes / 1024:.1f} KB" if size_bytes else "0.0 KB"
            except NotImplementedError:
                size = "N/A"
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not get size for {path}: {e}")
                size = "Error"
            except Exception as e:
                logger.warning(f"Unexpected error getting size for {path}: {e}")
                size = "Error"

            pipeline_info.append(
                {
                    "name": name,
                    "path": path,
                    "mod_time": mod_time,
                    "size": size,
                }
            )

        return pipeline_info

    # --- Public listing helpers ---

    def list_pipeline_info(self) -> list[dict[str, Any]]:
        """Get metadata for all available pipelines.

        Returns:
            list[dict[str, Any]]: Pipeline metadata dictionaries.
        """
        return self.collect_pipeline_info()

    def list_pipelines(self) -> list[str]:
        """Get the discovered pipeline names.

        Returns:
            list[str]: Canonical pipeline names.
        """
        return self.get_names()

    @property
    def pipelines(self) -> list[str]:
        """Get a list of discovered pipeline names."""
        return self.get_names()
