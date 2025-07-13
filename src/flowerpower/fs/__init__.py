import importlib

has_orjson = importlib.util.find_spec("orjson") is not None
has_polars = importlib.util.find_spec("polars") is not None

if has_orjson and has_polars:
    from .ext import AbstractFileSystem
else:
    from fsspec import AbstractFileSystem

# from .. import settings  # noqa: E402
from .base import get_protocol  # noqa: E402
from .base import DirFileSystem, get_filesystem, get_storage_options_and_fs
from .storage_options import AwsStorageOptions  # noqa: E402
from .storage_options import AzureStorageOptions  # noqa: E402
from .storage_options import BaseStorageOptions  # noqa: E402
from .storage_options import GcsStorageOptions  # noqa: E402
from .storage_options import GitHubStorageOptions  # noqa: E402
from .storage_options import GitLabStorageOptions, StorageOptions  # noqa: E402

__all__ = [
    "get_filesystem",
    "get_storage_options_and_fs",
    "get_protocol",
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
