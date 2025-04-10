import base64
import inspect
import os
import posixpath
from pathlib import Path
from urllib import parse
import fsspec
import requests
from fsspec import filesystem
from fsspec.implementations.cache_mapper import AbstractCacheMapper
from fsspec.implementations.cached import SimpleCacheFileSystem
from fsspec.implementations.dirfs import DirFileSystem
from fsspec.implementations.memory import MemoryFile
from fsspec.utils import infer_storage_options
from loguru import logger

from .ext import AbstractFileSystem
from .storage_options import BaseStorageOptions
from .storage_options import from_dict as storage_options_from_dict


class FileNameCacheMapper(AbstractCacheMapper):
    def __init__(self, directory):
        self.directory = directory

    def __call__(self, path: str) -> str:
        os.makedirs(
            posixpath.dirname(posixpath.join(self.directory, path)), exist_ok=True
        )
        return path


class MonitoredSimpleCacheFileSystem(SimpleCacheFileSystem):
    def __init__(self, **kwargs):
        # kwargs["cache_storage"] = posixpath.join(
        #    kwargs.get("cache_storage"), kwargs.get("fs").protocol[0]
        # )
        self._verbose = kwargs.get("verbose", False)
        super().__init__(**kwargs)
        self._mapper = FileNameCacheMapper(kwargs.get("cache_storage"))

    def _check_file(self, path):
        self._check_cache()
        cache_path = self._mapper(path)
        for storage in self.storage:
            fn = posixpath.join(storage, cache_path)
            if posixpath.exists(fn):
                return fn
            if self._verbose:
                logger.info(f"Downloading {self.protocol[0]}://{path}")

    # def glob(self, path):
    #    return [self._strip_protocol(path)]

    def size(self, path):
        cached_file = self._check_file(self._strip_protocol(path))
        if cached_file is None:
            return self.fs.size(path)
        else:
            return posixpath.getsize(cached_file)

    def sync(self, reload: bool = False):
        if reload:
            self.clear_cache()
        content = self.glob("**/*")
        [self.open(f).close() for f in content if self.isfile(f)]

    def __getattribute__(self, item):
        """
        Custom attribute access to delegate to the underlying filesystem or class as needed.
        Optimized for clarity, reduced redundancy, and robust error handling.
        """
        _special_methods = {
            "size", "glob", "sync", "load_cache", "_open", "save_cache", "close_and_update",
            "__init__", "__getattribute__", "__reduce__", "_make_local_details", "open",
            "cat", "cat_file", "cat_ranges", "get", "read_block", "tail", "head", "info",
            "ls", "exists", "isfile", "isdir", "_check_file", "_check_cache", "_mkcache",
            "clear_cache", "clear_expired_cache", "pop_from_cache", "local_file",
            "_paths_from_path", "get_mapper", "open_many", "commit_many", "hash_name",
            "__hash__", "__eq__", "to_json", "to_dict", "cache_size", "pipe_file", "pipe",
            "start_transaction", "end_transaction"
        }
        if item in _special_methods:
            method = getattr(type(self), item, None)
            if method is None:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")
            return lambda *args, **kw: method.__get__(self)(*args, **kw)

        if item == "__reduce_ex__":
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")

        if item == "transaction":
            return type(self).transaction.__get__(self)

        if item in {"_cache", "transaction_type"}:
            return getattr(type(self), item)

        if item == "__class__":
            return type(self)

        d = object.__getattribute__(self, "__dict__")
        fs = d.get("fs", None)

        if item in d:
            return d[item]

        if fs is not None:
            if hasattr(fs, "__dict__") and item in fs.__dict__:
                return fs.__dict__[item]
            cls = type(fs)
            if hasattr(cls, item):
                m = getattr(cls, item)
                # Only bind if m is a function or descriptor and has __get__ attribute
                if (inspect.isfunction(m) or inspect.isdatadescriptor(m)):
                    if (not hasattr(m, "__self__") or getattr(m, "__self__", None) is None) and hasattr(m, "__get__"):
                        return m.__get__(fs, cls)  # type: ignore[attr-defined]
                return m
            if hasattr(fs, item):
                return getattr(fs, item)
            raise AttributeError(f"'{type(fs).__name__}' object has no attribute '{item}'")

        try:
            return super().__getattribute__(item)
        except AttributeError as e:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'") from e


class GitLabFileSystem(AbstractFileSystem):
    def __init__(
        self,
        project_name: str | None = None,
        project_id: str | None = None,
        access_token: str | None = None,
        branch: str = "main",
        base_url: str = "https://gitlab.com",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.project_name = project_name
        self.project_id = project_id
        self.access_token = access_token
        self.branch = branch
        self.base_url = base_url.rstrip("/")
        self._validate_init()
        if not self.project_id:
            self.project_id = self._get_project_id()

    def _validate_init(self):
        if not self.project_id and not self.project_name:
            raise ValueError("Either 'project_id' or 'project_name' must be provided")

    def _get_project_id(self):
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

    def _open(self, path, mode="rb", block_size=None, autocommit=True, *args, **kwargs):  # type: ignore[override]
        # Signature matches AbstractFileSystem._open (ignore static type checker)
        if mode != "rb":
            raise NotImplementedError("Only read mode is supported")

        url = (
            f"{self.base_url}/api/v4/projects/{self.project_id}/repository/files/"
            f"{parse.quote_plus(path)}?ref={self.branch}"
        )
        headers = {"PRIVATE-TOKEN": self.access_token}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            file_content = base64.b64decode(response.json()["content"])
            return MemoryFile(None, None, file_content)
        else:
            response.raise_for_status()

    def _ls(self, path, detail=False, **kwargs):
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
    """
    Get a filesystem based on the given path and storage options.

    Args:
        path: Path to the filesystem.
        storage_options: Storage options as a dataclass or dict.
        dirfs: If True, return a DirFileSystem.
        cached: If True, use a cached filesystem.
        cache_storage: Path to the cache storage.
        fs: An existing filesystem instance.
        **storage_options_kwargs: Additional keyword arguments for the storage options.

    Returns:
        An fsspec-compatible filesystem instance.

    Raises:
        ValueError: If path or protocol is not provided or cannot be inferred.
    """
    if fs is not None:
        if cached:
            if hasattr(fs, "is_cache_fs") and getattr(fs, "is_cache_fs", False):
                return fs
            return MonitoredSimpleCacheFileSystem(fs=fs, cache_storage=cache_storage)

        if dirfs:
            if hasattr(fs, "protocol") and getattr(fs, "protocol", None) == "dir":
                return fs
            return DirFileSystem(path=path, fs=fs)

    if path is None:
        raise ValueError("Path must be provided to infer storage options.")

    pp = infer_storage_options(str(path) if isinstance(path, Path) else path)
    protocol = pp.get("protocol")
    if protocol is None:
        raise ValueError("Protocol could not be inferred from the path.")

    if protocol in {"file", "local"}:
        fs = filesystem(protocol)
        # Mark as cache fs only if attribute exists
        if dirfs:
            fs = DirFileSystem(path=path, fs=fs)
        if fs is None:
            raise RuntimeError("Failed to create a filesystem instance.")
        return fs

    host = pp.get("host", "")
    subpath = pp.get("path", "").lstrip("/")
    if len(host) and host not in subpath:
        subpath = posixpath.join(host, subpath)

    if isinstance(storage_options, dict):
        storage_options = storage_options_from_dict(protocol, storage_options)

    if storage_options is None:
        storage_options = storage_options_from_dict(protocol, storage_options_kwargs)

    fs = storage_options.to_filesystem()
    # Only set is_cache_fs if it exists (for custom cache fs)
    if dirfs and len(subpath):
        fs = DirFileSystem(path=subpath, fs=fs)
    if cached:
        if cache_storage is None:
            cache_storage = (Path.cwd() / (subpath or "")).as_posix()
        fs = MonitoredSimpleCacheFileSystem(fs=fs, cache_storage=cache_storage)

    if fs is None:
        raise RuntimeError("Failed to create a filesystem instance.")

    return fs
