import importlib
import posixpath
import sys
from types import TracebackType

from fsspec_utils import AbstractFileSystem, BaseStorageOptions, filesystem
from loguru import logger
from munch import Munch

from ..settings import CONFIG_DIR, PIPELINES_DIR
from ..cfg import PipelineConfig, ProjectConfig
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
        
    ):
        self._base_dir = base_dir
        self._storage_options = storage_options
        if fs is None:
            fs = filesystem(self._base_dir, **self._storage_options)
        self._fs = fs
        

        self._setup_paths()
        self._setup_directories()
        self._add_modules_path()

    def _setup_paths(self) -> None:
        """Set up configuration and pipeline directory paths."""
        self._cfg_dir = CONFIG_DIR
        self._pipelines_dir = PIPELINES_DIR

    def _setup_directories(self) -> None:
        """Set up required directories with proper error handling."""
        try:
            self._fs.makedirs(f"{self._cfg_dir}/pipelines", exist_ok=True)
            self._fs.makedirs(self._pipelines_dir, exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.error(f"Error creating directories: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating directories: {e}")
            raise

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
