import base64
import inspect
import os
import posixpath
import urllib
from pathlib import Path
from typing import Any

import fsspec
import requests
from fsspec import filesystem
from fsspec.implementations.cache_mapper import AbstractCacheMapper
from fsspec.implementations.cached import SimpleCacheFileSystem
from fsspec.implementations.dirfs import DirFileSystem
from fsspec.implementations.memory import MemoryFile
from fsspec.utils import infer_storage_options
from loguru import logger

from ..utils.logging import setup_logging
from . import has_orjson, has_polars

if has_orjson and has_polars:
    from .ext import AbstractFileSystem
else:
    from fsspec import AbstractFileSystem

from .storage_options import BaseStorageOptions
from .storage_options import from_dict as storage_options_from_dict

setup_logging()


class FileNameCacheMapper(AbstractCacheMapper):
    """Maps remote file paths to local cache paths while preserving directory structure.

    This cache mapper maintains the original file path structure in the cache directory,
    creating necessary subdirectories as needed.

    Attributes:
        directory (str): Base directory for cached files

    Example:
        >>> # Create cache mapper for S3 files
        >>> mapper = FileNameCacheMapper("/tmp/cache")
        >>>
        >>> # Map remote path to cache path
        >>> cache_path = mapper("bucket/data/file.csv")
        >>> print(cache_path)  # Preserves structure
        'bucket/data/file.csv'
    """

    def __init__(self, directory: str):
        """Initialize cache mapper with base directory.

        Args:
            directory: Base directory where cached files will be stored
        """
        self.directory = directory

    def __call__(self, path: str) -> str:
        """Map remote file path to cache file path.

        Creates necessary subdirectories in the cache directory to maintain
        the original path structure.

        Args:
            path: Original file path from remote filesystem

        Returns:
            str: Cache file path that preserves original structure

        Example:
            >>> mapper = FileNameCacheMapper("/tmp/cache")
            >>> # Maps maintain directory structure
            >>> print(mapper("data/nested/file.txt"))
            'data/nested/file.txt'
        """
        os.makedirs(
            posixpath.dirname(posixpath.join(self.directory, path)), exist_ok=True
        )
        return path


class MonitoredSimpleCacheFileSystem(SimpleCacheFileSystem):
    """Enhanced caching filesystem with monitoring and improved path handling.

    This filesystem extends SimpleCacheFileSystem to provide:
    - Verbose logging of cache operations
    - Improved path mapping for cache files
    - Enhanced synchronization capabilities
    - Better handling of parallel operations

    Attributes:
        _verbose (bool): Whether to print verbose cache operations
        _mapper (FileNameCacheMapper): Maps remote paths to cache paths
        storage (list[str]): List of cache storage locations
        fs (AbstractFileSystem): Underlying filesystem being cached

    Example:
        >>> from fsspec import filesystem
        >>> # Create monitored cache for S3
        >>> s3 = filesystem("s3", key="ACCESS_KEY", secret="SECRET_KEY")
        >>> cached_fs = MonitoredSimpleCacheFileSystem(
        ...     fs=s3,
        ...     cache_storage="/tmp/s3_cache",
        ...     verbose=True
        ... )
        >>>
        >>> # Read file (downloads and caches)
        >>> with cached_fs.open("bucket/data.csv") as f:
        ...     data = f.read()
        Downloading s3://bucket/data.csv
        >>>
        >>> # Second read uses cache
        >>> with cached_fs.open("bucket/data.csv") as f:
        ...     data = f.read()  # No download message
    """

    def __init__(self, **kwargs: Any):
        """Initialize monitored cache filesystem.

        Args:
            **kwargs: Configuration options including:
                fs (AbstractFileSystem): Filesystem to cache
                cache_storage (str): Cache directory path
                verbose (bool): Enable verbose logging
                And any other SimpleCacheFileSystem options

        Example:
            >>> # Cache with custom settings
            >>> cached_fs = MonitoredSimpleCacheFileSystem(
            ...     fs=remote_fs,
            ...     cache_storage="/tmp/cache",
            ...     verbose=True,
            ...     same_names=True  # Use original filenames
            ... )
        """
        self._verbose = kwargs.get("verbose", False)
        super().__init__(**kwargs)
        self._mapper = FileNameCacheMapper(kwargs.get("cache_storage"))

    def _check_file(self, path: str) -> str | None:
        """Check if file exists in cache and download if needed.

        Args:
            path: Path to file in the remote filesystem

        Returns:
            str | None: Path to cached file if found/downloaded, None otherwise

        Example:
            >>> fs = MonitoredSimpleCacheFileSystem(
            ...     fs=remote_fs,
            ...     cache_storage="/tmp/cache"
            ... )
            >>> cached_path = fs._check_file("data.csv")
            >>> print(cached_path)
            '/tmp/cache/data.csv'
        """
        self._check_cache()
        cache_path = self._mapper(path)
        for storage in self.storage:
            fn = posixpath.join(storage, cache_path)
            if posixpath.exists(fn):
                return fn
            if self._verbose:
                logger.info(f"Downloading {self.protocol[0]}://{path}")

    def size(self, path: str) -> int:
        """Get size of file in bytes.

        Checks cache first, falls back to remote filesystem.

        Args:
            path: Path to file

        Returns:
            int: Size of file in bytes

        Example:
            >>> fs = MonitoredSimpleCacheFileSystem(
            ...     fs=remote_fs,
            ...     cache_storage="/tmp/cache"
            ... )
            >>> size = fs.size("large_file.dat")
            >>> print(f"File size: {size} bytes")
        """
        cached_file = self._check_file(self._strip_protocol(path))
        if cached_file is None:
            return self.fs.size(path)
        else:
            return posixpath.getsize(cached_file)

    def sync_cache(self, reload: bool = False) -> None:
        """Synchronize cache with remote filesystem.

        Downloads all files in remote path to cache if not present.

        Args:
            reload: Whether to force reload all files, ignoring existing cache

        Example:
            >>> fs = MonitoredSimpleCacheFileSystem(
            ...     fs=remote_fs,
            ...     cache_storage="/tmp/cache"
            ... )
            >>> # Initial sync
            >>> fs.sync_cache()
            >>>
            >>> # Force reload all files
            >>> fs.sync_cache(reload=True)
        """
        if reload:
            self.clear_cache()
        content = self.glob("**/*")
        [self.open(f).close() for f in content if self.isfile(f)]

    def __getattribute__(self, item):
        if item in {
            # new items
            "size",
            "glob",
            "sync_cache",
            # previous
            "load_cache",
            "_open",
            "save_cache",
            "close_and_update",
            "__init__",
            "__getattribute__",
            "__reduce__",
            "_make_local_details",
            "open",
            "cat",
            "cat_file",
            "cat_ranges",
            "get",
            "read_block",
            "tail",
            "head",
            "info",
            "ls",
            "exists",
            "isfile",
            "isdir",
            "_check_file",
            "_check_cache",
            "_mkcache",
            "clear_cache",
            "clear_expired_cache",
            "pop_from_cache",
            "local_file",
            "_paths_from_path",
            "get_mapper",
            "open_many",
            "commit_many",
            "hash_name",
            "__hash__",
            "__eq__",
            "to_json",
            "to_dict",
            "cache_size",
            "pipe_file",
            "pipe",
            "start_transaction",
            "end_transaction",
        }:
            # all the methods defined in this class. Note `open` here, since
            # it calls `_open`, but is actually in superclass
            return lambda *args, **kw: getattr(type(self), item).__get__(self)(
                *args, **kw
            )
        if item in ["__reduce_ex__"]:
            raise AttributeError
        if item in ["transaction"]:
            # property
            return type(self).transaction.__get__(self)
        if item in ["_cache", "transaction_type"]:
            # class attributes
            return getattr(type(self), item)
        if item == "__class__":
            return type(self)
        d = object.__getattribute__(self, "__dict__")
        fs = d.get("fs", None)  # fs is not immediately defined
        if item in d:
            return d[item]
        elif fs is not None:
            if item in fs.__dict__:
                # attribute of instance
                return fs.__dict__[item]
            # attributed belonging to the target filesystem
            cls = type(fs)
            m = getattr(cls, item)
            if (inspect.isfunction(m) or inspect.isdatadescriptor(m)) and (
                not hasattr(m, "__self__") or m.__self__ is None
            ):
                # instance method
                return m.__get__(fs, cls)
            return m  # class method or attribute
        else:
            # attributes of the superclass, while target is being set up
            return super().__getattribute__(item)


class GitLabFileSystem(AbstractFileSystem):
    """FSSpec-compatible filesystem interface for GitLab repositories.

    Provides access to files in GitLab repositories through the GitLab API,
    supporting read operations with authentication.

    Attributes:
        project_name (str): Name of the GitLab project
        project_id (str): ID of the GitLab project
        access_token (str): GitLab personal access token
        branch (str): Git branch to read from
        base_url (str): GitLab instance URL

    Example:
        >>> # Access public project
        >>> fs = GitLabFileSystem(
        ...     project_name="my-project",
        ...     access_token="glpat-xxxx"
        ... )
        >>>
        >>> # Read file contents
        >>> with fs.open("path/to/file.txt") as f:
        ...     content = f.read()
        >>>
        >>> # List directory
        >>> files = fs.ls("path/to/dir")
        >>>
        >>> # Access enterprise GitLab
        >>> fs = GitLabFileSystem(
        ...     project_id="12345",
        ...     access_token="glpat-xxxx",
        ...     base_url="https://gitlab.company.com",
        ...     branch="develop"
        ... )
    """

    def __init__(
        self,
        project_name: str | None = None,
        project_id: str | None = None,
        access_token: str | None = None,
        branch: str = "main",
        base_url: str = "https://gitlab.com",
        **kwargs,
    ):
        """Initialize GitLab filesystem.

        Args:
            project_name: Name of the GitLab project. Required if project_id not provided.
            project_id: ID of the GitLab project. Required if project_name not provided.
            access_token: GitLab personal access token for authentication.
                Required for private repositories.
            branch: Git branch to read from. Defaults to "main".
            base_url: GitLab instance URL. Defaults to "https://gitlab.com".
            **kwargs: Additional arguments passed to AbstractFileSystem.

        Raises:
            ValueError: If neither project_name nor project_id is provided
            requests.RequestException: If GitLab API request fails
        """
        super().__init__(**kwargs)
        self.project_name = project_name
        self.project_id = project_id
        self.access_token = access_token
        self.branch = branch
        self.base_url = base_url.rstrip("/")
        self._validate_init()
        if not self.project_id:
            self.project_id = self._get_project_id()

    def _validate_init(self) -> None:
        """Validate initialization parameters.

        Ensures that either project_id or project_name is provided.

        Raises:
            ValueError: If neither project_id nor project_name is provided
        """
        if not self.project_id and not self.project_name:
            raise ValueError("Either 'project_id' or 'project_name' must be provided")

    def _get_project_id(self) -> str:
        """Retrieve project ID from GitLab API using project name.

        Makes an API request to search for projects and find the matching project ID.

        Returns:
            str: The GitLab project ID

        Raises:
            ValueError: If project not found
            requests.RequestException: If API request fails
        """
        url = f"{self.base_url}/api/v4/projects"
        headers = {"PRIVATE-TOKEN": self.access_token}
        params = {"search": self.project_name}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            projects = response.json()
            for project in projects:
                if project["name"] == self.project_name:
                    return project["id"]
            raise ValueError(f"Project '{self.project_name}' not found")
        else:
            response.raise_for_status()

    def _open(self, path: str, mode: str = "rb", **kwargs) -> MemoryFile:
        """Open a file from GitLab repository.

        Retrieves file content from GitLab API and returns it as a memory file.

        Args:
            path: Path to file within repository
            mode: File open mode. Only "rb" (read binary) is supported.
            **kwargs: Additional arguments (unused)

        Returns:
            MemoryFile: File-like object containing file content

        Raises:
            NotImplementedError: If mode is not "rb"
            requests.RequestException: If API request fails

        Example:
            >>> fs = GitLabFileSystem(project_id="12345", access_token="glpat-xxxx")
            >>> with fs.open("README.md") as f:
            ...     content = f.read()
            ...     print(content.decode())
        """
        if mode != "rb":
            raise NotImplementedError("Only read mode is supported")

        url = (
            f"{self.base_url}/api/v4/projects/{self.project_id}/repository/files/"
            f"{urllib.parse.quote_plus(path)}?ref={self.branch}"
        )
        headers = {"PRIVATE-TOKEN": self.access_token}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            file_content = base64.b64decode(response.json()["content"])
            return MemoryFile(None, None, file_content)
        else:
            response.raise_for_status()

    def _ls(self, path: str, detail: bool = False, **kwargs) -> list[str] | list[dict]:
        """List contents of a directory in GitLab repository.

        Args:
            path: Directory path within repository
            detail: Whether to return detailed information about each entry.
                If True, returns list of dicts with file metadata.
                If False, returns list of filenames.
            **kwargs: Additional arguments (unused)

        Returns:
            list[str] | list[dict]: List of file/directory names or detailed info

        Raises:
            requests.RequestException: If API request fails

        Example:
            >>> fs = GitLabFileSystem(project_id="12345", access_token="glpat-xxxx")
            >>> # List filenames
            >>> files = fs.ls("docs")
            >>> print(files)
            ['README.md', 'API.md']
            >>>
            >>> # List with details
            >>> details = fs.ls("docs", detail=True)
            >>> for item in details:
            ...     print(f"{item['name']}: {item['type']}")
        """
        url = f"{self.base_url}/api/v4/projects/{self.project_id}/repository/tree?path={path}&ref={self.branch}"
        headers = {"PRIVATE-TOKEN": self.access_token}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            files = response.json()
            if detail:
                return files
            else:
                return [file["name"] for file in files]
        else:
            response.raise_for_status()


try:
    fsspec.register_implementation("gitlab", GitLabFileSystem)
except ValueError as e:
    _ = e


# Original ls Methode speichern
dirfs_ls_o = DirFileSystem.ls
mscf_ls_o = MonitoredSimpleCacheFileSystem.ls


# Neue ls Methode definieren
def dir_ls_p(self, path, detail=False, **kwargs):
    return dirfs_ls_o(self, path, detail=detail, **kwargs)


def mscf_ls_p(self, path, detail=False, **kwargs):
    return mscf_ls_o(self, path, detail=detail, **kwargs)


# patchen
DirFileSystem.ls = dir_ls_p
MonitoredSimpleCacheFileSystem.ls = mscf_ls_p


def get_filesystem(
    path: str | Path | None = None,
    storage_options: BaseStorageOptions | dict[str, str] | None = None,
    dirfs: bool = True,
    cached: bool = False,
    cache_storage: str | None = None,
    fs: AbstractFileSystem | None = None,
    **storage_options_kwargs,
) -> AbstractFileSystem:
    """Get a filesystem instance based on path or configuration.

    This function creates and configures a filesystem instance based on the provided path
    and options. It supports various filesystem types including local, S3, GCS, Azure,
    and Git-based filesystems.

    Args:
        path: URI or path to the filesystem location. Examples:
            - Local: "/path/to/data"
            - S3: "s3://bucket/path"
            - GCS: "gs://bucket/path"
            - Azure: "abfs://container/path"
            - GitHub: "github://org/repo/path"
        storage_options: Configuration options for the filesystem. Can be:
            - BaseStorageOptions object with protocol-specific settings
            - Dictionary of key-value pairs for authentication/configuration
            - None to use environment variables or default credentials
        dirfs: Whether to wrap filesystem in DirFileSystem for path-based operations.
            Set to False when you need direct protocol-specific features.
        cached: Whether to enable local caching of remote files.
            Useful for frequently accessed remote files.
        cache_storage: Directory path for cached files. Defaults to path-based location
            in current directory if not specified.
        fs: Existing filesystem instance to wrap with caching or dirfs.
            Use this to customize an existing filesystem instance.
        **storage_options_kwargs: Additional keyword arguments for storage options.
            Alternative to passing storage_options dictionary.

    Returns:
        AbstractFileSystem: Configured filesystem instance with requested features.

    Raises:
        ValueError: If storage protocol or options are invalid
        FSSpecError: If filesystem initialization fails
        ImportError: If required filesystem backend is not installed

    Example:
        >>> # Local filesystem
        >>> fs = get_filesystem("/path/to/data")
        >>>
        >>> # S3 with credentials
        >>> fs = get_filesystem(
        ...     "s3://bucket/data",
        ...     storage_options={
        ...         "key": "ACCESS_KEY",
        ...         "secret": "SECRET_KEY"
        ...     }
        ... )
        >>>
        >>> # Cached GCS filesystem
        >>> fs = get_filesystem(
        ...     "gs://bucket/data",
        ...     storage_options=GcsStorageOptions(
        ...         token="service_account.json"
        ...     ),
        ...     cached=True,
        ...     cache_storage="/tmp/gcs_cache"
        ... )
        >>>
        >>> # Azure with environment credentials
        >>> fs = get_filesystem(
        ...     "abfs://container/data",
        ...     storage_options=AzureStorageOptions.from_env()
        ... )
        >>>
        >>> # Wrap existing filesystem
        >>> base_fs = filesystem("s3", key="ACCESS", secret="SECRET")
        >>> cached_fs = get_filesystem(
        ...     fs=base_fs,
        ...     cached=True
        ... )
    """
    if fs is not None:
        if dirfs:
            base_path = path.split("://")[-1]
            if fs.protocol == "dir":
                if base_path != fs.path:
                    fs = DirFileSystem(
                        path=posixpath.join(
                            fs.path, base_path.replace(fs.path, "").lstrip("/")
                        ),
                        fs=fs.fs,
                    )
            else:
                fs = DirFileSystem(path=base_path, fs=fs)
        if cached:
            if fs.is_cache_fs:
                return fs
            fs = MonitoredSimpleCacheFileSystem(fs=fs, cache_storage=cache_storage)

        return fs

    pp = infer_storage_options(str(path) if isinstance(path, Path) else path)
    protocol = (
        storage_options_kwargs.get("protocol", None)
        or (
            storage_options.get("protocol", None)
            if isinstance(storage_options, dict)
            else getattr(storage_options, "protocol", None)
        )
        or pp.get("protocol", "file")
    )

    if protocol == "file" or protocol == "local":
        fs = filesystem(protocol)
        fs.is_cache_fs = False
        if dirfs:
            fs = DirFileSystem(path=path, fs=fs)
            fs.is_cache_fs = False
        return fs

    host = pp.get("host", "")
    path = pp.get("path", "").lstrip("/")
    if len(host) and host not in path:
        path = posixpath.join(host, path)
    if "." in path:
        path = posixpath.dirname(path)

    if isinstance(storage_options, dict):
        storage_options = storage_options_from_dict(protocol, storage_options)

    if storage_options is None:
        storage_options = storage_options_from_dict(protocol, storage_options_kwargs)

    fs = storage_options.to_filesystem()
    fs.is_cache_fs = False
    if dirfs and len(path):
        fs = DirFileSystem(path=path, fs=fs)
        fs.is_cache_fs = False
    if cached:
        if cache_storage is None:
            cache_storage = (Path.cwd() / path).as_posix()
        fs = MonitoredSimpleCacheFileSystem(fs=fs, cache_storage=cache_storage)
        fs.is_cache_fs = True

    return fs
