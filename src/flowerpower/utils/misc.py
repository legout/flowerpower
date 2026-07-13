"""Miscellaneous utility helpers for shared runtime concerns."""

from __future__ import annotations

import importlib
import sys
from collections.abc import Iterator, KeysView, Mapping
from types import SimpleNamespace
from typing import Any

from fsspeckit import AbstractFileSystem, filesystem


class DictNamespace(SimpleNamespace, Mapping[str, Any]):
    """A SimpleNamespace subclass that preserves dict-style bracket access.

    This lets nested dictionaries be exposed as attribute-accessible
    namespaces while keeping ``PARAMS['key']`` working for backward
    compatibility.
    """

    def __getitem__(self, key: str) -> Any:
        try:
            return self.__dict__[key]
        except KeyError:
            raise KeyError(key) from None

    def __iter__(self) -> Iterator[str]:
        yield from self.__dict__

    def __len__(self) -> int:
        return len(self.__dict__)

    def keys(self) -> KeysView[str]:
        return self.__dict__.keys()

    def to_dict(self) -> dict[str, Any]:
        """Return a recursively converted plain dictionary."""
        return {
            key: _namespace_to_dict(value) for key, value in self.__dict__.items()
        }

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Mapping):
            return self.to_dict() == dict(other)
        return super().__eq__(other)


def _namespace_to_dict(obj: Any) -> Any:
    if isinstance(obj, DictNamespace):
        return obj.to_dict()
    if isinstance(obj, list):
        return [_namespace_to_dict(item) for item in obj]
    return obj


def dict_to_namespace(obj: Any) -> Any:
    """Recursively convert nested dicts into attribute-accessible namespaces.

    Lists are processed recursively; all other values are returned unchanged.
    The resulting namespace still supports dict-style bracket access so that
    existing code using ``PARAMS['key']`` continues to work.

    Args:
        obj: A value to convert. Only dicts are wrapped; everything else is
            returned as-is (lists are recursively converted).

    Returns:
        A DictNamespace for dicts, a list of converted values for lists, or
        the original value for other types.
    """
    if isinstance(obj, dict):
        ns = DictNamespace()
        for key, value in obj.items():
            ns.__dict__[key] = dict_to_namespace(value)
        return ns
    if isinstance(obj, list):
        return [dict_to_namespace(item) for item in obj]
    return obj


def load_module(name: str, reload: bool = False):
    """
    Load a module.

    Args:
        name (str): The name of the module.

    Returns:
        module: The loaded module.
    """
    if name in sys.modules:
        if reload:
            return importlib.reload(sys.modules[name])
        return sys.modules[name]
    return importlib.import_module(name)


def get_filesystem(
    fs: AbstractFileSystem | None = None, fs_type: str = "file"
) -> AbstractFileSystem:
    """Return an existing filesystem or create one for ``fs_type``."""
    if fs is None:
        fs = filesystem(fs_type)
    return fs


__all__ = [
    "DictNamespace",
    "dict_to_namespace",
    "get_filesystem",
    "load_module",
]
