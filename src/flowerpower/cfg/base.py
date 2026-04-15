import copy
import json
from collections import OrderedDict
from typing import Any, ClassVar, Self

import msgspec
from fsspeckit import AbstractFileSystem, BaseStorageOptions, filesystem

from ..utils.misc import get_filesystem
from ..utils.security import SecurityError, validate_file_path
from .exceptions import ConfigLoadError, ConfigSaveError


class BaseConfig(msgspec.Struct, kw_only=True):
    _filesystem_cache: ClassVar[
        OrderedDict[tuple[str | None, str], AbstractFileSystem]
    ] = OrderedDict()
    _filesystem_cache_maxsize: ClassVar[int] = 32

    @classmethod
    def _get_cached_filesystem(
        cls,
        base_dir: str | None,
        storage_options: dict | BaseStorageOptions | None = None,
    ) -> AbstractFileSystem:
        """Get a cached filesystem instance.

        Args:
            base_dir: Base directory for the filesystem.
            storage_options: Storage options used to create the filesystem.

        Returns:
            Cached filesystem instance.
        """
        normalized_options = cls._normalize_storage_options(storage_options)
        cache_key = (
            base_dir,
            cls._storage_options_cache_key(normalized_options),
        )
        cached_fs = cls._filesystem_cache.get(cache_key)
        if cached_fs is not None:
            cls._filesystem_cache.move_to_end(cache_key)
            return cached_fs

        cls._filesystem_cache[cache_key] = filesystem(
                base_dir,
                storage_options=normalized_options,
                cached=True,
                dirfs=True,
            )
        if len(cls._filesystem_cache) > cls._filesystem_cache_maxsize:
            cls._filesystem_cache.popitem(last=False)
        return cls._filesystem_cache[cache_key]

    @classmethod
    def _normalize_storage_options(
        cls,
        storage_options: dict | BaseStorageOptions | None,
    ) -> dict[str, Any] | None:
        """Normalize storage options to a plain dictionary."""
        if storage_options is None:
            return None

        if isinstance(storage_options, BaseStorageOptions):
            normalized = storage_options.to_dict(with_protocol=True)
        elif hasattr(storage_options, "toDict"):
            normalized = storage_options.toDict()
        else:
            normalized = dict(storage_options)

        return normalized or None

    @classmethod
    def _storage_options_cache_key(
        cls, storage_options: dict[str, Any] | None
    ) -> str:
        """Create a stable cache key for storage options."""
        if not storage_options:
            return "{}"

        try:
            return json.dumps(storage_options, sort_keys=True, default=str)
        except TypeError:
            return repr(storage_options)

    def to_dict(self) -> dict[str, Any]:
        # Convert to dictionary, handling special cases like type objects
        result = {}
        for field in self.__struct_fields__:
            value = getattr(self, field)
            if isinstance(value, type):
                # Convert type objects to string representation
                result[field] = str(value)
            elif hasattr(value, "__struct_fields__"):
                # Recursively convert nested msgspec structs
                result[field] = value.to_dict()
            elif hasattr(value, "toDict"):
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
                    elif hasattr(item, "toDict"):
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
            if hasattr(value, "toDict"):
                # Convert Munch objects to regular dict
                result[key] = value.toDict()
            elif isinstance(value, dict):
                # Recursively handle nested dictionaries
                result[key] = self._convert_dict_recursively(value)
            elif isinstance(value, list):
                # Handle lists within dictionaries
                converted_list = []
                for item in value:
                    if hasattr(item, "toDict"):
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
            ConfigSaveError: If saving the configuration fails or the path is invalid.
        """
        # Validate the path to prevent directory traversal
        if fs is not None and "://" in str(path):
            validated_path = path
        else:
            try:
                validated_path = validate_file_path(
                    path, allow_absolute=False, allow_relative=True
                )
            except SecurityError as e:
                raise ConfigSaveError(
                    f"Path validation failed: {e}", path=path, original_error=e
                ) from e

        # Default to fsspec.filesystem when fs is not provided (testable/mocked)
        if fs is None:
            try:
                import fsspec  # type: ignore

                fs = fsspec.filesystem("file")
            except Exception:
                # Fallback to project helper if fsspec is unavailable in context
                fs = get_filesystem(fs)
        try:
            with fs.open(str(validated_path), "wb") as f:
                f.write(msgspec.yaml.encode(self, order="deterministic"))
        except NotImplementedError:
            # Surface underlying capability error as-is (expected by tests)
            raise
        except Exception as e:
            raise ConfigSaveError(
                f"Failed to write configuration to {validated_path}",
                path=validated_path,
                original_error=e,
            ) from e

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
            ConfigLoadError: If loading the configuration fails or the path is invalid.
        """
        # Validate the path to prevent directory traversal (skip for fsspec URLs when fs provided)
        if fs is not None and "://" in str(path):
            validated_path = path
        else:
            try:
                validated_path = validate_file_path(
                    path, allow_absolute=False, allow_relative=True
                )
            except SecurityError as e:
                raise ConfigLoadError(
                    f"Path validation failed: {e}", path=path, original_error=e
                ) from e

        fs = get_filesystem(fs)
        try:
            # tests expect default mode when fs provided
            with fs.open(str(validated_path)) as f:
                return msgspec.yaml.decode(f.read(), type=cls, strict=True)
        except Exception as e:
            raise ConfigLoadError(
                f"Failed to load configuration from {validated_path}",
                path=validated_path,
                original_error=e,
            ) from e

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
                elif hasattr(current_value, "__struct_fields__"):
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
