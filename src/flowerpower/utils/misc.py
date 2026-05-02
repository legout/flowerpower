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
"""Miscellaneous utility helpers.

This module keeps a small compatibility surface for older imports while the
actual image-viewing implementation lives in :mod:`flowerpower.utils.visualization`.
"""

import importlib
import sys

from fsspeckit import AbstractFileSystem, filesystem

from .visualization import (
    _cleanup_temp_file,
    _create_temp_image_file,
    _open_image_viewer,
    _validate_image_format,
    view_img,
)


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
    "view_img",
]
