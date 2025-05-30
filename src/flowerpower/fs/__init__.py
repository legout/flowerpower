import importlib

has_orjson = importlib.util.find_spec("orjson") is not None
has_polars = importlib.util.find_spec("polars") is not None

if has_orjson and has_polars:
    from .ext import AbstractFileSystem
else:
    from fsspec import AbstractFileSystem

from .base import DirFileSystem, get_filesystem  # noqa: E402
from .storage_options import AwsStorageOptions  # noqa: E402
from .storage_options import AzureStorageOptions  # noqa: E402
from .storage_options import GcsStorageOptions  # noqa: E402
from .storage_options import (BaseStorageOptions, GitHubStorageOptions,
                              GitLabStorageOptions, StorageOptions)

__all__ = [
    "get_filesystem",
    "DirFileSystem",
    "AbstractFileSystem",
    "StorageOptions",
    "AwsStorageOptions",
    "AzureStorageOptions",
    "GcsStorageOptions",
    "GitHubStorageOptions",
    "GitLabStorageOptions",
    "BaseStorageOptions",
]
