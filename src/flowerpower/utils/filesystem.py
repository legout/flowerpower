"""
Filesystem utilities for FlowerPower pipeline management.

This module provides helper classes and functions for common filesystem operations
used throughout the FlowerPower codebase.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from fsspeckit import AbstractFileSystem, filesystem
from loguru import logger
from .security import validate_file_path


class FilesystemHelper:
    """
    Helper class for filesystem operations with caching and error handling.

    This class provides centralized filesystem operations with proper error handling
    and logging for common operations like directory creation, path resolution,
    and filesystem initialization.
    """

    def __init__(self, base_dir: str, storage_options: Optional[Dict[str, Any]] = None):
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
        self._fs_cache: Dict[str, AbstractFileSystem] = {}

    def get_filesystem(self, cached: bool = False, cache_storage: Optional[str] = None) -> AbstractFileSystem:
        """
        Get a filesystem instance with optional caching.

        Args:
            cached: Whether to use cached filesystem
            cache_storage: Storage path for cached filesystem

        Returns:
            AbstractFileSystem: Configured filesystem instance
        """
        cache_key = f"{self._base_dir}_{cached}_{cache_storage}"

        if cache_key not in self._fs_cache:
            if cached and cache_storage:
                # Ensure cache storage directory exists
                cache_path = Path(cache_storage)
                cache_path.mkdir(parents=True, exist_ok=True)

            self._fs_cache[cache_key] = filesystem(
                self._base_dir,
                storage_options=self._storage_options,
                cached=cached,
                cache_storage=cache_storage,
            )

        return self._fs_cache[cache_key]

    def ensure_directories_exist(
        self,
        fs: AbstractFileSystem,
        *directories: str,
        exist_ok: bool = True
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
                raise RuntimeError(f"Failed to create directory {directory}: {e}") from e
            except Exception as e:
                logger.error(f"Unexpected error creating directory {directory}: {e}")
                raise RuntimeError(f"Unexpected filesystem error for {directory}: {e}") from e

    def resolve_path(self, fs: AbstractFileSystem, *path_parts: str) -> str:
        """
        Resolve a path in the filesystem.

        Args:
            fs: Filesystem instance
            *path_parts: Path components to join

        Returns:
            str: Resolved path
        """
        if hasattr(fs, 'path'):
            base_path = fs.path
        else:
            base_path = self._base_dir

        resolved_path = fs.join(base_path, *path_parts)
        # Validate resolved path for security
        validate_file_path(resolved_path, allow_relative=True)
        return resolved_path

    def clean_directory(
        self,
        fs: AbstractFileSystem,
        *paths: str,
        recursive: bool = True
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

    def sync_filesystem(self, fs: AbstractFileSystem) -> None:
        """
        Sync filesystem cache if applicable.

        Args:
            fs: Filesystem instance to sync
        """
        if hasattr(fs, 'is_cache_fs') and fs.is_cache_fs:
            fs.sync_cache()

            # Log sync information if available
            if hasattr(fs, '_mapper') and hasattr(fs, 'cache_path'):
                logger.debug(
                    f"Synced filesystem cache: {fs._mapper.directory} -> {fs.cache_path}"
                )

    def get_project_path(self, fs: AbstractFileSystem) -> str:
        """
        Get the project path for the filesystem.

        Args:
            fs: Filesystem instance

        Returns:
            str: Project path
        """
        if hasattr(fs, 'is_cache_fs') and fs.is_cache_fs:
            project_path = fs._mapper.directory
        else:
            project_path = getattr(fs, 'path', self._base_dir)
        
        # Validate project path for security
        validate_file_path(project_path, allow_relative=True)
        return project_path

    def clear_cache(self) -> None:
        """Clear the filesystem cache."""
        self._fs_cache.clear()


def create_filesystem_helper(
    base_dir: str,
    storage_options: Optional[Dict[str, Any]] = None
) -> FilesystemHelper:
    """
    Factory function to create a FilesystemHelper instance.

    Args:
        base_dir: Base directory for filesystem operations
        storage_options: Storage options for filesystem access

    Returns:
        FilesystemHelper: Configured helper instance
    """
    return FilesystemHelper(base_dir, storage_options)