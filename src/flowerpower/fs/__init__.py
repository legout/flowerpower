import importlib
import os
import posixpath

has_orjson = importlib.util.find_spec("orjson") is not None
has_polars = importlib.util.find_spec("polars") is not None

if has_orjson and has_polars:
    from .ext import AbstractFileSystem
else:
    from fsspec import AbstractFileSystem

from .. import settings  # noqa: E402
from .base import DirFileSystem, get_filesystem  # noqa: E402
from .storage_options import AwsStorageOptions  # noqa: E402
from .storage_options import AzureStorageOptions  # noqa: E402
from .storage_options import BaseStorageOptions  # noqa: E402
from .storage_options import GcsStorageOptions  # noqa: E402
from .storage_options import GitHubStorageOptions  # noqa: E402
from .storage_options import GitLabStorageOptions, StorageOptions


def get_storage_options_and_fs(
    base_dir: str,
    storage_options: BaseStorageOptions | dict | None = None,
    fs: AbstractFileSystem | None = None,
) -> tuple[BaseStorageOptions | dict | None, AbstractFileSystem | None]:
    """Get storage options and filesystem instance."""
    if storage_options is not None:
        cached = True
        cache_storage = posixpath.join(
            posixpath.expanduser(settings.CACHE_DIR),
            base_dir.split("://")[-1],
        )
        os.makedirs(cache_storage, exist_ok=True)
    else:
        cached = False
        cache_storage = None
    if not fs:
        fs = get_filesystem(
            base_dir,
            storage_options=storage_options,
            cached=cached,
            cache_storage=cache_storage,
        )

    storage_options = (
        storage_options or fs.storage_options
        if fs.protocol != "dir"
        else fs.fs.storage_options
    )
    return fs, storage_options


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
