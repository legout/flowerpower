import copy
from pathlib import Path
from typing import Any, Self, Optional
from functools import lru_cache

import msgspec
from fsspeckit import AbstractFileSystem, filesystem
from munch import Munch
from ..utils.misc import get_filesystem
from ..utils.security import validate_file_path as security_validate_file_path
from .exceptions import ConfigLoadError, ConfigSaveError, ConfigPathError


def validate_file_path(path: str) -> str:
    """
    Validate a file path to prevent directory traversal attacks.
    
    Args:
        path: The file path to validate
        
    Returns:
        str: The validated path
        
    Raises:
        ConfigPathError: If the path contains directory traversal attempts
    """
    try:
        # Use the comprehensive security validation
        validated_path = security_validate_file_path(
            path,
            allow_absolute=False,  # Config files should be relative
            allow_relative=True
        )
        return str(validated_path)
    except Exception as e:
        # Convert security errors to config path errors for consistency
        raise ConfigPathError(f"Invalid file path: {path}. {str(e)}", path=path) from e


class BaseConfig(msgspec.Struct, kw_only=True):
    # Class-level cache for filesystem instances
    _fs_cache = {}
    
    @classmethod
    @lru_cache(maxsize=32)
    def _get_cached_filesystem(cls, base_dir: str, storage_options_hash: int) -> AbstractFileSystem:
        """Get a cached filesystem instance.
        
        Args:
            base_dir: Base directory for the filesystem.
            storage_options_hash: Hash of storage options for cache key.
            
        Returns:
            Cached filesystem instance.
        """
        cache_key = (base_dir, storage_options_hash)
        if cache_key not in cls._fs_cache:
            cls._fs_cache[cache_key] = filesystem(base_dir, cached=True, dirfs=True)
        return cls._fs_cache[cache_key]
    
    @classmethod
    def _hash_storage_options(cls, storage_options: dict | None) -> int:
        """Create a hash of storage options for caching.
        
        Args:
            storage_options: Storage options to hash.
            
        Returns:
            Hash of storage options.
        """
        if not storage_options:
            return hash(())
        
        # Convert to frozenset of items for consistent hashing
        try:
            return hash(frozenset(sorted(storage_options.items())))
        except TypeError:
            # If items are not hashable, use string representation
            return hash(str(sorted(storage_options.items())))
    def to_dict(self) -> dict[str, Any]:
        # Convert to dictionary, handling special cases like type objects
        result = {}
        for field in self.__struct_fields__:
            value = getattr(self, field)
            if isinstance(value, type):
                # Convert type objects to string representation
                result[field] = str(value)
            elif hasattr(value, '__struct_fields__'):
                # Recursively convert nested msgspec structs
                result[field] = value.to_dict()
            elif hasattr(value, 'toDict'):
                # Handle Munch objects by converting to regular dict
                result[field] = value.toDict()
            elif isinstance(value, dict):
                # Handle regular dictionaries that might contain Munch objects
                result[field] = self._convert_dict_recursively(value)
            elif isinstance(value, list):
                # Handle lists that might contain type objects or Munch objects
                converted_list = []
                for item in value:
                    if isinstance(item, type):
                        converted_list.append(str(item))
                    elif hasattr(item, 'toDict'):
                        # Handle Munch objects in lists
                        converted_list.append(item.toDict())
                    elif isinstance(item, dict):
                        # Handle dictionaries in lists
                        converted_list.append(self._convert_dict_recursively(item))
                    else:
                        converted_list.append(item)
                result[field] = converted_list
            else:
                result[field] = value
        return result
    
    def _convert_dict_recursively(self, d: dict) -> dict:
        """Recursively convert dictionaries, handling Munch objects."""
        result = {}
        for key, value in d.items():
            if hasattr(value, 'toDict'):
                # Convert Munch objects to regular dict
                result[key] = value.toDict()
            elif isinstance(value, dict):
                # Recursively handle nested dictionaries
                result[key] = self._convert_dict_recursively(value)
            elif isinstance(value, list):
                # Handle lists within dictionaries
                converted_list = []
                for item in value:
                    if hasattr(item, 'toDict'):
                        converted_list.append(item.toDict())
                    elif isinstance(item, dict):
                        converted_list.append(self._convert_dict_recursively(item))
                    else:
                        converted_list.append(item)
                result[key] = converted_list
            else:
                result[key] = value
        return result

    def to_yaml(self, path: str, fs: AbstractFileSystem | None = None) -> None:
        """
        Converts the instance to a YAML file.

        Args:
            path: The path to the YAML file.
            fs: An optional filesystem instance to use for file operations.

        Raises:
            ConfigSaveError: If saving the configuration fails.
            ConfigPathError: If the path contains directory traversal attempts.
        """
        # Validate the path to prevent directory traversal
        try:
            validated_path = validate_file_path(path)
        except ConfigPathError as e:
            raise ConfigSaveError(f"Path validation failed: {e}", path=path, original_error=e)
            
        # Default to fsspec.filesystem when fs is not provided (testable/mocked)
        if fs is None:
            try:
                import fsspec  # type: ignore
                fs = fsspec.filesystem("file")
            except Exception:
                # Fallback to project helper if fsspec is unavailable in context
                fs = get_filesystem(fs)
        try:
            with fs.open(validated_path, "wb") as f:
                f.write(msgspec.yaml.encode(self, order="deterministic"))
        except NotImplementedError as e:
            # Surface underlying capability error as-is (expected by tests)
            raise e
        except Exception as e:
            raise ConfigSaveError(f"Failed to write configuration to {validated_path}", path=validated_path, original_error=e)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseConfig":
        """
        Converts a dictionary to an instance of the class.
        Args:
            data: The dictionary to convert.

        Returns:
            An instance of the class with the values from the dictionary.
        """
        return msgspec.convert(data, cls)

    @classmethod
    def from_yaml(cls, path: str, fs: AbstractFileSystem | None = None) -> "BaseConfig":
        """
        Loads a YAML file and converts it to an instance of the class.

        Args:
            path: The path to the YAML file.
            fs: An optional filesystem instance to use for file operations.

        Returns:
            An instance of the class with the values from the YAML file.

        Raises:
            ConfigLoadError: If loading the configuration fails.
            ConfigPathError: If the path contains directory traversal attempts.
        """
        # Validate the path to prevent directory traversal (skip for fsspec URLs when fs provided)
        if fs is not None and "://" in path:
            validated_path = path
        else:
            try:
                validated_path = validate_file_path(path)
            except ConfigPathError as e:
                raise ConfigLoadError(f"Path validation failed: {e}", path=path, original_error=e)
            
        fs = get_filesystem(fs)
        try:
            # tests expect default mode when fs provided
            with fs.open(validated_path) as f:
                return msgspec.yaml.decode(f.read(), type=cls, strict=True)
        except Exception as e:
            raise ConfigLoadError(f"Failed to load configuration from {validated_path}", path=validated_path, original_error=e)

    def _apply_dict_updates(self, target: Self, d: dict[str, Any]) -> None:
        """
        Helper method to apply dictionary updates to a target instance.
        
        Args:
            target: The target instance to apply updates to.
            d: The dictionary containing updates to apply.
        """
        for k, v in d.items():
            if hasattr(target, k):
                current_value = getattr(target, k)
                if isinstance(current_value, dict) and isinstance(v, dict):
                    # For dictionaries, avoid mutating original nested dicts
                    new_dict = dict(current_value)
                    new_dict.update(v)
                    setattr(target, k, new_dict)
                elif hasattr(current_value, '__struct_fields__'):
                    # For nested msgspec structs, create a new instance with merged values
                    setattr(target, k, current_value.merge_dict(v))
                else:
                    # For primitive values, direct assignment is fine
                    setattr(target, k, v)
            else:
                # Use object.__setattr__ to bypass msgspec.Struct's restrictions
                object.__setattr__(target, k, v)

    def update(self, d: dict[str, Any]) -> None:
        """
        Updates this instance with values from the provided dictionary.
        
        Args:
            d: The dictionary containing updates to apply.
        """
        self._apply_dict_updates(self, d)

    def merge_dict(self, d: dict[str, Any]) -> Self:
        """
        Creates a copy of this instance and updates the copy with values
        from the provided dictionary. The original instance (self) is not modified.

        Args:
            d: The dictionary to get values from.

        Returns:
            A new instance of the struct with updated values.
        """
        # Use shallow copy for better performance
        self_copy = copy.copy(self)
        self._apply_dict_updates(self_copy, d)
        return self_copy

    def merge(self, source: Self) -> Self:
        """
        Creates a copy of this instance and updates the copy with values
        from the source struct, only if the source field's value is not
        its default value. The original instance (self) is not modified.

        Args:
            source: The msgspec.Struct instance of the same type to get values from.

        Returns:
            A new instance of the struct with updated values.

        Raises:
            TypeError: If source is not of the same type as self.
        """
        if type(self) is not type(source):
            raise TypeError(
                f"Source must be an instance of {type(self).__name__}, not {type(source).__name__}"
            )

        updated_instance = copy.copy(self)

        # Get default values if they exist
        defaults = getattr(source, "__struct_defaults__", {})

        for field in source.__struct_fields__:
            source_value = getattr(source, field)
            has_explicit_default = field in defaults
            is_default_value = False

            if has_explicit_default:
                is_default_value = source_value == defaults[field]
            else:
                is_default_value = source_value is None

            if not is_default_value:
                setattr(updated_instance, field, source_value)

        return updated_instance
