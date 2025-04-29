import importlib.metadata

from .cfg import Config, PipelineConfig, ProjectConfig
from .flowerpower import init as init_project  # noqa: E402
from .job_queue import JobQueueManager
from .pipeline import PipelineManager

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
