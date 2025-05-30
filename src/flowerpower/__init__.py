import importlib.metadata

from .cfg import Config, PipelineConfig, ProjectConfig
from .flowerpower import FlowerPower, FlowerPowerProject
from .flowerpower import init as init_project  # noqa: E402
from .job_queue import JobQueueManager  # noqa: E402
from .pipeline import PipelineManager

__version__ = importlib.metadata.version("FlowerPower")

__all__ = [
    "__version__",
    "init_project",
    "FlowerPower",
    "FlowerPowerProject",
    "PipelineManager",
    "JobQueueManager",
    "Config",
    "ProjectConfig",
    "PipelineConfig",
    "PipelineConfig",
]
