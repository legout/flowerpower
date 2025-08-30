import importlib.metadata

from .cfg import Config, PipelineConfig, ProjectConfig
from .flowerpower import FlowerPower, FlowerPowerProject, create_project
from .pipeline import PipelineManager

__version__ = importlib.metadata.version("FlowerPower")

__all__ = [
    "__version__",
    "create_project",
    "FlowerPower",
    "FlowerPowerProject",
    "PipelineManager",
    "Config",
    "ProjectConfig",
    "PipelineConfig",
]
