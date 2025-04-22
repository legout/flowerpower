import importlib

has_orjson = importlib.util.find_spec("orjson") is not None

if has_orjson:
    from .ext import AbstractFileSystem
else:
    from fsspec import AbstractFileSystem

from .base import get_filesystem  # noqa: E402
from .storage_options import AwsStorageOptions  # noqa: E402
from .storage_options import ( # noqa: E402
    AzureStorageOptions,
    BaseStorageOptions,
    GcsStorageOptions,
    GitHubStorageOptions,
    GitLabStorageOptions,
    StorageOptions,
) 

__all__ = [
    "get_filesystem",
    "AbstractFileSystem",
    "StorageOptions",
    "AwsStorageOptions",
    "AzureStorageOptions",
    "GcsStorageOptions",
    "GitHubStorageOptions",
    "GitLabStorageOptions",
    "BaseStorageOptions",
]
