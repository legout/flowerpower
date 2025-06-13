import importlib
import posixpath
import sys
from types import TracebackType

from loguru import logger
from munch import Munch

from ..cfg import PipelineConfig, ProjectConfig
from ..fs import AbstractFileSystem, BaseStorageOptions, get_filesystem
from ..utils.logging import setup_logging

setup_logging()


def load_module(name: str, reload: bool = False):
    """
    Load a module.

    Args:
        name (str): The name of the module.

    Returns:
        module: The loaded module.
    """
    if name in sys.modules:
        if reload:
            return importlib.reload(sys.modules[name])
        return sys.modules[name]
    return importlib.import_module(name)


class BasePipeline:
    """
    Base class for all pipelines.
    """

    def __init__(
        self,
        base_dir: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions = {},
        fs: AbstractFileSystem | None = None,
        cfg_dir: str = "conf",
        pipelines_dir: str = "pipelines",
        job_queue_type: str | None = None,  # New parameter for worker backend
    ):
        self._base_dir = base_dir
        self._storage_options = storage_options
        if fs is None:
            fs = get_filesystem(self._base_dir, **self._storage_options)
        self._fs = fs
        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir
        self._job_queue_type = job_queue_type

        try:
            self._fs.makedirs(f"{self._cfg_dir}/pipelines", exist_ok=True)
            self._fs.makedirs(self._pipelines_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")

        self._add_modules_path()

    def __enter__(self) -> "BasePipeline":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass

    def _add_modules_path(self):
        """
        Sync the filesystem.

        Returns:
            None
        """
        if self._fs.is_cache_fs:
            self._fs.sync_cache()
            modules_path = posixpath.join(
                self._fs._mapper.directory, self._fs.cache_path, self._pipelines_dir
            )
        else:
            modules_path = posixpath.join(self._fs.path, self._pipelines_dir)
        if modules_path not in sys.path:
            sys.path.insert(0, modules_path)

    def _load_project_cfg(self) -> ProjectConfig:
        """
        Load the project configuration.

        Returns:
            ProjectConfig: The loaded project configuration.
        """
        return ProjectConfig.load(
            base_dir=self._base_dir,
            job_queue_type=self._job_queue_type,
            fs=self._fs,
            storage_options=self._storage_options,
        )

    def _load_pipeline_cfg(self, name: str) -> PipelineConfig:
        """
        Load the pipeline configuration.

        Args:
            name (str): The name of the pipeline.

        Returns:
            PipelineConfig: The loaded pipeline configuration.
        """
        return PipelineConfig.load(
            base_dir=self._base_dir,
            name=name,
            fs=self._fs,
            storage_options=self._storage_options,
        )
