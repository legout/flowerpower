import base64
import inspect
import os
import urllib
from pathlib import Path

import fsspec
import requests
from fsspec import url_to_fs
from fsspec.implementations.cache_mapper import AbstractCacheMapper
from fsspec.implementations.cached import SimpleCacheFileSystem
from fsspec.implementations.dirfs import DirFileSystem
from fsspec.implementations.memory import MemoryFile
from fsspec.spec import AbstractFileSystem
from loguru import logger


class FileNameCacheMapper(AbstractCacheMapper):
    def __init__(self, directory):
        self.directory = directory

    def __call__(self, path: str) -> str:
        os.makedirs(os.path.dirname(os.path.join(self.directory, path)), exist_ok=True)
        return path


class MonitoredSimpleCacheFileSystem(SimpleCacheFileSystem):
    def __init__(self, **kwargs):
        # kwargs["cache_storage"] = os.path.join(
        #    kwargs.get("cache_storage"), kwargs.get("fs").protocol[0]
        # )
        self._verbose = kwargs.get("verbose", False)
        super().__init__(**kwargs)
        self._mapper = FileNameCacheMapper(kwargs.get("cache_storage"))

    def _check_file(self, path):
        self._check_cache()
        cache_path = self._mapper(path)
        for storage in self.storage:
            fn = os.path.join(storage, cache_path)
            if os.path.exists(fn):
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
            return os.path.getsize(cached_file)

    def sync(self, reload: bool = False):
        if reload:
            self.clear_cache()
        content = self.glob("**/*")
        [self.open(f).close() for f in content if self.isfile(f)]

    def __getattribute__(self, item):
        if item in {
            # new items
            "size",
            "glob",
            "sync",
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


class GitLabFileSystem(AbstractFileSystem):
    def __init__(
        self,
        project_name,
        access_token,
        branch="main",
        base_url="https://gitlab.com",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.project_name = project_name
        self.access_token = access_token
        self.branch = branch
        self.base_url = base_url.rstrip("/")
        self.project_id = self._get_project_id()

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

    def _open(self, path, mode="rb", **kwargs):
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


def _s3_storage_options_to_kwargs(storage_options):
    storage_options["client_kwargs"] = storage_options.get("client_kwargs", {})
    storage_options["s3_additional_kwargs"] = storage_options.get(
        "s3_additional_kwargs", {}
    )
    for key in storage_options:
        if key.lower() in ["aws_access_key_id", "access_key"]:
            storage_options["key"] = storage_options.pop(key)
        if key.lower() in ["aws_secret_access_key", "secret_access_key"]:
            storage_options["secret"] = storage_options.pop(key)
        if key.lower() in ["aws_region", "region_name", "region", "aws_default_region"]:
            storage_options["client_kwargs"].update(
                {"region": storage_options.pop(key)}
            )
        if key.lower() in ["aws_session_token", "session_token"]:
            storage_options["token"] = storage_options.pop(key)
        if key.lower() in ["aws_endpoint_url", "endpoint", "aws_endpoint"]:
            storage_options["endpoint_url"] = storage_options.pop(key)
        if key.lower() in ["allow_invalid_certificates"]:
            storage_options["client_kwargs"]["verify"] = (
                storage_options.pop(key) != "true"
            )
        if key.lower() in ["aws_allow_http", "allow_http"]:
            storage_options["client_kwargs"]["use_ssl"] = (
                storage_options.pop(key) != "true"
            )

    return storage_options


def get_filesystem(path: str | None = None, **storage_options) -> DirFileSystem:
    storage_options = _s3_storage_options_to_kwargs(storage_options)
    if path is None:
        path = "file://."
    fs, path = url_to_fs(path, **storage_options)

    if fs.protocol[0] == "file" or fs.protocol[0] == "local":
        fs = DirFileSystem(path=path, fs=fs)
        # fs.temp_dir = None
        fs.is_cache_fs = False
        return fs

    # temp_dir = tempfile.TemporaryDirectory()
    fs = MonitoredSimpleCacheFileSystem(
        fs=DirFileSystem(path=path, fs=fs), cache_storage=(Path.cwd() / path).as_posix()
    )  # , cache_storage=
    # fs.temp_dir = temp_dir
    fs.is_cache_fs = True
    return fs
