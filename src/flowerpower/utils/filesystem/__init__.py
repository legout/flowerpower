import importlib

has_pyarrow = importlib.util.find_spec("pyarrow") is not None

if has_pyarrow:
    from .ext import AbstractFileSystem
else:
    from fsspec import AbstractFileSystem

from .base import get_filesystem
