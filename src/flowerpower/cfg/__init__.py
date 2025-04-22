from pathlib import Path

import msgspec
from munch import Munch

from ..fs import AbstractFileSystem, get_filesystem
from .base import BaseConfig
from .pipeline import PipelineConfig
from .project import ProjectConfig


class Config(BaseConfig):
    pipeline: PipelineConfig = msgspec.field(default_factory=PipelineConfig)
    project: ProjectConfig = msgspec.field(default_factory=ProjectConfig)
    fs: AbstractFileSystem | None = None
    base_dir: str | Path | None = None
    storage_options: dict | Munch = msgspec.field(default_factory=Munch)

    @classmethod
    def load(
        cls,
        base_dir: str = ".",
        name: str | None = None,
        pipeline_name: str | None = None,
        worker_type: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | Munch = Munch(),
    ):
        if fs is None:
            fs = get_filesystem(base_dir, cached=True, dirfs=True, **storage_options)
        project = ProjectConfig.load(
            base_dir=base_dir,
            name=name,
            worker_type=worker_type,
            fs=fs,
            storage_options=storage_options,
        )
        pipeline = PipelineConfig.load(
            base_dir=base_dir,
            name=pipeline_name,
            fs=fs,
            storage_options=storage_options,
        )

        return cls(
            base_dir=base_dir,
            pipeline=pipeline,
            project=project,
            fs=fs,
            storage_options=storage_options,
        )

    def save(
        self,
        project: bool = False,
        pipeline: bool = True,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | Munch = Munch(),
    ):
        if fs is None and self.fs is None:
            self.fs = get_filesystem(
                self.base_dir, cached=True, dirfs=True, **storage_options
            )

        if not self.fs.exists("conf"):
            self.fs.makedirs("conf")

        if pipeline:
            self.fs.makedirs("conf/pipelines", exist_ok=True)
            h_params = self.pipeline.pop("h_params") if self.pipeline.h_params else None
            self.pipeline.to_yaml(
                path=f"conf/pipelines/{self.pipeline.name}.yml", fs=self.fs
            )
            if h_params:
                self.pipeline.h_params = h_params
        if project:
            self.project.to_yaml("conf/project.yml", self.fs)


def load(
    base_dir: str,
    name: str | None = None,
    pipeline_name: str | None = None,
    storage_options: dict | Munch = Munch(),
    fs: AbstractFileSystem | None = None,
):
    return Config.load(
        name=name,
        pipeline_name=pipeline_name,
        base_dir=base_dir,
        storage_options=storage_options,
        fs=fs,
    )


def save(
    config: Config,
    project: bool = False,
    pipeline: bool = True,
    fs: AbstractFileSystem | None = None,
    storage_options: dict | Munch = Munch(),
):
    config.save(
        project=project, pipeline=pipeline, fs=fs, storage_options=storage_options
    )
