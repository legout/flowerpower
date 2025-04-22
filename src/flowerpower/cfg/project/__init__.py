import msgspec
from munch import Munch

from ...fs import AbstractFileSystem, get_filesystem
from ..base import BaseConfig
from .adapter import AdapterConfig
from .worker import WorkerConfig


class ProjectConfig(BaseConfig):
    name: str | None = msgspec.field(default=None)
    worker: WorkerConfig = msgspec.field(default_factory=WorkerConfig)
    adapter: AdapterConfig = msgspec.field(default_factory=AdapterConfig)

    @classmethod
    def load(
        cls,
        base_dir: str = ".",
        name: str | None = None,
        worker_type: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | Munch = Munch(),
    ):
        if fs is None:
            fs = get_filesystem(base_dir, cached=True, dirfs=True, **storage_options)
        if fs.exists("conf/project.yml"):
            project = ProjectConfig.from_yaml(path="conf/project.yml", fs=fs)
        else:
            project = ProjectConfig(name=name)
        if worker_type is not None:
            if worker_type != project.worker.type:
                project.worker.update_type(worker_type)

        return project

    def save(
        self,
        base_dir: str = ".",
        fs: AbstractFileSystem | None = None,
        storage_options: dict | Munch = Munch(),
    ):
        if fs is None:
            fs = get_filesystem(base_dir, cached=True, dirfs=True, **storage_options)

        fs.makedirs("conf", exist_ok=True)
        self.to_yaml(path="conf/project.yml", fs=fs)
