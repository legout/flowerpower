"""
Filesystem utilities for FlowerPower pipeline management.

This module provides helper classes and functions for common filesystem operations
used throughout the FlowerPower codebase.
"""

import posixpath
import sys
from collections.abc import Iterable
from typing import Any

from fsspeckit import AbstractFileSystem
from loguru import logger

from .security import validate_file_path


def find_first_existing_path(
    fs: AbstractFileSystem,
    candidates: Iterable[str],
    *,
    purpose: str = "path",
) -> str | None:
    """Return the first existing candidate path, skipping probe failures.

    Some filesystem backends raise while probing specific paths via ``exists()``.
    Callers using fallback candidate lists should treat those probe failures as a
    miss and continue checking later candidates.

    Args:
        fs: Filesystem used for existence checks.
        candidates: Candidate paths in priority order.
        purpose: Short label used for debug logging.

    Returns:
        The first candidate that exists, otherwise ``None``.
    """
    for candidate in candidates:
        try:
            if fs.exists(candidate):
                return candidate
        except Exception as error:
            logger.debug(f"Skipping unreadable {purpose} candidate {candidate}: {error}")
    return None


def resolve_project_path(
    fs: AbstractFileSystem,
    base_dir: str | None = None,
    *,
    sync_cache: bool = True,
) -> str:
    """Resolve the local project path used for runtime imports.

    Cache-backed filesystems sometimes expose the synced project directory via
    ``fs._mapper.directory``. Other filesystem implementations only provide a
    ``path`` attribute, and some expose neither. This helper centralizes the
    fallback order so callers do not need to rely on brittle private attributes.

    Args:
        fs: Filesystem instance.
        base_dir: Fallback project directory when the filesystem does not expose
            a usable local path.
        sync_cache: Whether to synchronize cache-backed filesystems before
            resolving their local project path.

    Returns:
        Normalized project path suitable for ``sys.path`` insertion.
    """
    project_path: str | None = None

    if getattr(fs, "is_cache_fs", False):
        sync_cache_fn = getattr(fs, "sync_cache", None)
        if sync_cache and callable(sync_cache_fn):
            try:
                sync_cache_fn()
            except Exception as error:
                logger.debug(f"Failed to sync filesystem cache before import setup: {error}")

        mapper = getattr(fs, "_mapper", None)
        project_path = getattr(mapper, "directory", None)

    if not project_path:
        project_path = getattr(fs, "path", None) or base_dir or "."

    resolved = str(project_path)
    if "://" in resolved:
        return resolved.rstrip("/") or resolved
    return posixpath.normpath(resolved)


def add_modules_path(
    fs: AbstractFileSystem,
    pipelines_dir: str,
    base_dir: str | None = None,
) -> None:
    """Add pipeline module paths to Python's ``sys.path``.

    This is a shared utility extracted from PipelineRegistry so that any
    component that needs to import pipeline modules at runtime can set up
    the correct import paths.

    Args:
        fs: The filesystem instance (may be a cache FS).
        pipelines_dir: Relative path to the pipelines directory
                      (e.g. ``"pipelines"`` or ``"flows"``).
        base_dir: Fallback base directory when the filesystem does not expose
                  a ``path`` attribute.
    """
    project_path = resolve_project_path(fs, base_dir)
    if "://" in project_path:
        logger.debug(
            f"Skipping sys.path update for non-local project path {project_path}"
        )
        return

    modules_path = posixpath.normpath(posixpath.join(project_path, pipelines_dir or ""))
    known_paths = {posixpath.normpath(str(path)) for path in sys.path}

    if project_path not in known_paths:
        sys.path.insert(0, project_path)
        known_paths.add(project_path)

    if modules_path != project_path and modules_path not in known_paths:
        sys.path.insert(0, modules_path)


def format_pipeline_file_path(name: str) -> str:
    """Format a pipeline name for use in file paths.

    Replaces dots with forward slashes to create directory hierarchies
    for grouped pipelines, and hyphens with underscores for valid file names.

    Args:
        name: The raw pipeline name.

    Returns:
        The formatted pipeline name suitable for file paths.

    Examples:
        >>> format_pipeline_file_path("my-pipeline")
        'my_pipeline'
        >>> format_pipeline_file_path("sub.module")
        'sub/module'
        >>> format_pipeline_file_path("my-pipeline.sub")
        'my_pipeline/sub'
    """
    return name.replace(".", "/").replace("-", "_")


def format_pipeline_module_path(name: str) -> str:
    """Format a pipeline name for use as a Python module import path.

    Replaces hyphens with underscores for valid Python identifiers,
    while keeping dots as module separators.

    Args:
        name: The raw pipeline name.

    Returns:
        The formatted pipeline name suitable for module imports.

    Examples:
        >>> format_pipeline_module_path("my-pipeline")
        'my_pipeline'
        >>> format_pipeline_module_path("sub.module")
        'sub.module'
        >>> format_pipeline_module_path("my-pipeline.sub")
        'my_pipeline.sub'
    """
    return name.replace("-", "_")


def format_pipeline_package_root(pipelines_dir: str | None) -> str:
    """Convert a pipeline directory fragment into a Python package path.

    Args:
        pipelines_dir: Relative pipelines directory such as ``"pipelines"`` or
            ``"pkg/flows"``.

    Returns:
        A dotted Python package path, or an empty string when modules live at the
        project root.

    Examples:
        >>> format_pipeline_package_root("pipelines")
        'pipelines'
        >>> format_pipeline_package_root("pkg/flows")
        'pkg.flows'
        >>> format_pipeline_package_root("")
        ''
    """
    normalized = posixpath.normpath(pipelines_dir or "")
    if normalized in ("", "."):
        return ""
    return normalized.replace("/", ".")


def get_project_config_paths(
    cfg_dir: str | None,
    *,
    extensions: tuple[str, ...] = (".yml", ".yaml"),
) -> list[str]:
    """Build candidate project-config paths.

    Args:
        cfg_dir: Configuration directory fragment.
        extensions: File extensions to generate in priority order.

    Returns:
        Candidate project config paths in lookup order, without duplicates.
    """
    root = cfg_dir or ""
    paths: list[str] = []
    seen: set[str] = set()

    for extension in extensions:
        filename = f"project{extension}"
        path = posixpath.join(root, filename) if root else filename
        if path not in seen:
            seen.add(path)
            paths.append(path)

    return paths


def get_pipeline_config_paths(
    pipeline_path: str,
    cfg_dir: str | None,
    pipelines_dir: str | None,
    *,
    extensions: tuple[str, ...] = (".yml", ".yaml"),
) -> list[str]:
    """Build candidate config paths for one pipeline.

    The canonical location is ``<cfg_dir>/<pipelines_dir>/<pipeline>.yml``. For
    backwards compatibility, callers may also look in ``<cfg_dir>/<pipeline>.yml``.

    Args:
        pipeline_path: Pipeline path already formatted for filesystem usage, e.g.
            ``"group/my_pipeline"``.
        cfg_dir: Configuration directory fragment.
        pipelines_dir: Pipelines directory fragment.
        extensions: File extensions to generate in priority order.

    Returns:
        Candidate paths in lookup order, without duplicates.
    """
    pipeline_path = pipeline_path.strip("/")
    roots = []
    canonical_root = (
        posixpath.join(cfg_dir, pipelines_dir)
        if cfg_dir
        else (pipelines_dir or "")
    )
    fallback_root = cfg_dir or ""

    for root in (canonical_root, fallback_root):
        if root not in roots:
            roots.append(root)

    paths: list[str] = []
    seen: set[str] = set()
    for root in roots:
        for extension in extensions:
            filename = f"{pipeline_path}{extension}"
            path = posixpath.join(root, filename) if root else filename
            if path not in seen:
                seen.add(path)
                paths.append(path)

    return paths


class FilesystemHelper:
    """
    Helper class for filesystem operations with caching and error handling.

    This class provides centralized filesystem operations with proper error handling
    and logging for common operations like directory creation, path resolution,
    and filesystem initialization.
    """

    def __init__(self, base_dir: str, storage_options: dict[str, Any] | None = None):
        """
        Initialize the filesystem helper.

        Args:
            base_dir: Base directory for filesystem operations
            storage_options: Storage options for filesystem access
        """
        # Validate base directory for security
        validate_file_path(base_dir, allow_relative=True)
        self._base_dir = base_dir
        self._storage_options = storage_options or {}


    def ensure_directories_exist(
        self, fs: AbstractFileSystem, *directories: str, exist_ok: bool = True
    ) -> None:
        """
        Ensure that the specified directories exist.

        Args:
            fs: Filesystem instance
            *directories: Directory paths to create
            exist_ok: Whether to ignore existing directories

        Raises:
            RuntimeError: If directory creation fails
        """
        for directory in directories:
            # Validate directory path for security
            validate_file_path(directory, allow_relative=True)
            try:
                fs.makedirs(directory, exist_ok=exist_ok)
            except (OSError, PermissionError) as e:
                logger.error(f"Error creating directory {directory}: {e}")
                raise RuntimeError(
                    f"Failed to create directory {directory}: {e}"
                ) from e
            except Exception as e:
                logger.error(f"Unexpected error creating directory {directory}: {e}")
                raise RuntimeError(
                    f"Unexpected filesystem error for {directory}: {e}"
                ) from e

    def clean_directory(
        self, fs: AbstractFileSystem, *paths: str, recursive: bool = True
    ) -> None:
        """
        Clean specified paths if they exist.

        Args:
            fs: Filesystem instance
            *paths: Paths to clean
            recursive: Whether to remove recursively
        """
        for path in paths:
            # Validate path for security before cleaning
            validate_file_path(path, allow_relative=True)
            if fs.exists(path):
                try:
                    fs.rm(path, recursive=recursive)
                except Exception as e:
                    logger.warning(f"Failed to clean path {path}: {e}")

    def get_project_path(self, fs: AbstractFileSystem) -> str:
        """
        Get the project path for the filesystem.

        Args:
            fs: Filesystem instance

        Returns:
            str: Project path
        """
        project_path = resolve_project_path(fs, self._base_dir)

        # Validate project path for security
        validate_file_path(project_path, allow_relative=True)
        return project_path

