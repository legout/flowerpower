"""Conditional filesystem interface import.

If 'orjson' is available, use the local AbstractFileSystem implementation.
Otherwise, fall back to fsspec's AbstractFileSystem.

Always expose get_filesystem from the local base module.
"""

from importlib.util import find_spec

has_orjson = find_spec("orjson") is not None

if has_orjson:
    from .ext import AbstractFileSystem
else:
    from fsspec import AbstractFileSystem

from .base import filesystem, AbstractFileSystem
from .storage_options import (
    AwsStorageOptions,
    StorageOptions,
    GitHubStorageOptions,
    GcsStorageOptions,
    AzureStorageOptions,
    GitLabStorageOptions,
    LocalStorageOptions,
    S3StorageOptions,
)
