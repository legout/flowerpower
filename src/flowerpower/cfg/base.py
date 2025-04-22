import copy
from typing import Any, Self

import msgspec
from fsspec import AbstractFileSystem, filesystem


class BaseConfig(msgspec.Struct, kw_only=True):
    def to_dict(self) -> dict[str, Any]:
        return msgspec.to_builtins(self)

    def to_yaml(self, path: str, fs: AbstractFileSystem | None = None) -> None:
        """
        Converts the instance to a YAML file.

        Args:
            path: The path to the YAML file.
            fs: An optional filesystem instance to use for file operations.

        Raises:
            NotImplementedError: If the filesystem does not support writing files.
        """
        if fs is None:
            fs = filesystem("file")
        try:
            with fs.open(path, "wb") as f:
                f.write(msgspec.yaml.encode(self, order="deterministic"))
                # yaml.dump(self.to_dict(), f, default_flow_style=False)
        except NotImplementedError:
            raise NotImplementedError("The filesystem does not support writing files.")

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

        """
        if fs is None:
            fs = filesystem("file")
        with fs.open(path) as f:
            # data = yaml.full_load(f)
            # return cls.from_dict(data)
            return msgspec.yaml.decode(f.read(), type=cls, strict=False)

    def update(self, d: dict[str, Any]) -> None:
        for k, v in d.items():
            if hasattr(self, k):
                current_value = getattr(self, k)
                if isinstance(current_value, dict) and isinstance(v, dict):
                    current_value.update(v)
                else:
                    setattr(self, k, v)
            else:
                setattr(self, k, v)

    def merge_dict(self, d: dict[str, Any]) -> Self:
        """
        Creates a copy of this instance and updates the copy with values
        from the provided dictionary, only if the dictionary field's value is not
        its default value. The original instance (self) is not modified.

        Args:
            d: The dictionary to get values from.

        Returns:
            A new instance of the struct with updated values.
        """
        self_copy = copy.copy(self)
        for k, v in d.items():
            if hasattr(self_copy, k):
                current_value = getattr(self_copy, k)
                if isinstance(current_value, dict) and isinstance(v, dict):
                    current_value.update(v)
                else:
                    setattr(self_copy, k, v)
            else:
                setattr(self_copy, k, v)
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
