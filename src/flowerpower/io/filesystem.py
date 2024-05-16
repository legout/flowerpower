from fsspec import AbstractFileSystem
from ..helpers import set_idl_credentials
from pydala.filesystem import FileSystem


def filesystem(**kwargs) -> AbstractFileSystem:
    profile = kwargs.get("profile", "local")
    if profile in [
        "mdsp",
        "mdsp-readonly",
        "inhub",
        "inhub-readonly",
    ]:
        set_idl_credentials()
    return FileSystem(**kwargs)
