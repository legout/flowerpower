import importlib.metadata

from .flowerpower import init as init_project  # noqa: E402

__version__ = importlib.metadata.version("FlowerPower")

__all__ = [
    "__version__",
    "init_project",
]
