"""Miscellaneous utility helpers for shared runtime concerns."""

import importlib
import sys

from fsspeckit import AbstractFileSystem, filesystem


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
    "get_filesystem",
    "load_module",
]
