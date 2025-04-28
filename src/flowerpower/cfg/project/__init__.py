import msgspec
from munch import Munch

from ...fs import AbstractFileSystem, get_filesystem
from ..base import BaseConfig
from .adapter import AdapterConfig
from .worker import WorkerConfig


class ProjectConfig(BaseConfig):
    """A configuration class for managing project-level settings in FlowerPower.

    This class handles project-wide configuration including worker and adapter settings.
    It supports loading from and saving to YAML files, with filesystem abstraction.

    Attributes:
        name (str | None): The name of the project.
        worker (WorkerConfig): Configuration for the worker component.
        adapter (AdapterConfig): Configuration for the adapter component.

    Example:
        ```python
        # Create a new project config
        project = ProjectConfig(name="my-project")

        # Load existing project config
        project = ProjectConfig.load(base_dir="path/to/project")

        # Save project config
        project.save(base_dir="path/to/project")
        ```
    """

    name: str | None = msgspec.field(default=None)
    worker: WorkerConfig = msgspec.field(default_factory=WorkerConfig)
    adapter: AdapterConfig = msgspec.field(default_factory=AdapterConfig)

    def __post_init__(self):
        if isinstance(self.worker, dict):
            self.worker = WorkerConfig.from_dict(self.worker)
        if isinstance(self.adapter, dict):
            self.adapter = AdapterConfig.from_dict(self.adapter)

    @classmethod
    def load(
        cls,
        base_dir: str = ".",
        name: str | None = None,
        worker_type: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | Munch = Munch(),
    ):
        """Load project configuration from a YAML file.

        Args:
            base_dir (str, optional): Base directory for the project. Defaults to ".".
            name (str | None, optional): Project name. Defaults to None.
            worker_type (str | None, optional): Type of worker to use. Defaults to None.
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Returns:
            ProjectConfig: Loaded project configuration.

        Example:
            ```python
            project = ProjectConfig.load(
                base_dir="my_project",
                name="pipeline1",
                worker_type="local"
                )
            ```
        """
        if fs is None:
            fs = get_filesystem(base_dir, cached=False, dirfs=True, **storage_options)
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
        """Save project configuration to a YAML file.

        Args:
            base_dir (str, optional): Base directory for the project. Defaults to ".".
            fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
            storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

        Example:
            ```python
            project_config.save(base_dir="my_project")
            ```
        """
        if fs is None:
            fs = get_filesystem(base_dir, cached=True, dirfs=True, **storage_options)

        fs.makedirs("conf", exist_ok=True)
        self.to_yaml(path="conf/project.yml", fs=fs)


def init_project_config(
    base_dir: str = ".",
    name: str | None = None,
    worker_type: str | None = None,
    fs: AbstractFileSystem | None = None,
    storage_options: dict | Munch = Munch(),
):
    """Initialize a new project configuration.

    This function creates a new project configuration and saves it to disk.

    Args:
        base_dir (str, optional): Base directory for the project. Defaults to ".".
        name (str | None, optional): Project name. Defaults to None.
        worker_type (str | None, optional): Type of worker to use. Defaults to None.
        fs (AbstractFileSystem | None, optional): Filesystem to use. Defaults to None.
        storage_options (dict | Munch, optional): Options for filesystem. Defaults to empty Munch.

    Returns:
        ProjectConfig: The initialized project configuration.

    Example:
        ```python
        project = init_project_config(
            base_dir="my_project",
            name="test_project",
            worker_type="local"
        )
        ```
    """
    project = ProjectConfig.load(
        base_dir=base_dir,
        name=name,
        worker_type=worker_type,
        fs=fs,
        storage_options=storage_options,
    )
    project.save(base_dir=base_dir, fs=fs, storage_options=storage_options)
    return project