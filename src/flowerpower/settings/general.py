import os

PIPELINES_DIR = os.getenv("FP_PIPELINES_DIR", "pipelines")
CONFIG_DIR = os.getenv("FP_CONFIG_DIR", "conf")
HOOKS_DIR = os.getenv("FP_HOOKS_DIR", "hooks")
CACHE_DIR = os.getenv("FP_CACHE_DIR", "~/.flowerpower/cache")
