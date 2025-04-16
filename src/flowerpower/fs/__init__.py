import importlib

has_orjson = importlib.util.find_spec("orjson") is not None

if has_orjson:
    from .ext import AbstractFileSystem
else:
    from fsspec import AbstractFileSystem

from .base import get_filesystem # noqa: F401
from .storage_options import StorageOptions, AwsStorageOptions, AzureStorageOptions, GcsStorageOptions, GitHubStorageOptions, GitLabStorageOptions # noqa: F401


__all__ = [
    "get_filesystem",
    "AbstractFileSystem",
    "StorageOptions",
    "AwsStorageOptions",
    "AzureStorageOptions",
    "GcsStorageOptions",
    "GitHubStorageOptions",
    "GitLabStorageOptions",
]
