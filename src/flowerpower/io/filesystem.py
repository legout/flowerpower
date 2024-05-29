from fsspec import AbstractFileSystem
from pydala.filesystem import FileSystem


def filesystem(**kwargs) -> AbstractFileSystem:
    profile = kwargs.pop("profile", "local")
    protocol = kwargs.pop("protocol", "s3")
    return FileSystem(profile=profile, protocol=protocol, **kwargs)


def s3(profile: str = "default", **kwargs):
    return filesystem(profile=profile, protocol="s3", **kwargs)


def local(**kwargs):
    return filesystem(protocol="file", **kwargs)


def gcs():
    pass
