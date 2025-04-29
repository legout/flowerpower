import importlib.metadata

from .flowerpower import init as init_project  # noqa: E402

from .pipeline import PipelineManager
from .job_queue import JobQueueManager
from .cfg import Config, ProjectConfig, PipelineConfig

__version__ = importlib.metadata.version("FlowerPower")

__all__ = [
    "__version__",
    "init_project",
    "PipelineManager",
    "JobQueueManager",
    "Config",
    "ProjectConfig",
    "PipelineConfig",
    "PipelineConfig",
]
