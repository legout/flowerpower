import importlib.util
import sys
import uuid
from pathlib import Path
from typing import Any

# RQ and RQ-Scheduler imports will be added here or in relevant modules later
# from redis import Redis
# from rq import Queue
# from rq_scheduler import Scheduler

from fsspec.spec import AbstractFileSystem
from loguru import logger

from .cfg import Config
from .fs import get_filesystem

# TODO: Refactor or remove these display functions to work with RQ/Redis
from .utils.scheduler import display_jobs, display_schedules, display_tasks


# Placeholder for potential future RQ/Redis related utility functions
# E.g., functions to get RQ queue instances, scheduler instances, fetch jobs, etc.

logger.warning(
    "APScheduler code removed. RQ/RQ-Scheduler integration pending in relevant modules (e.g., pipeline.py, cli)."
)

# Removed SchedulerManager class and APScheduler-specific functions.
# Removed backward compatibility wrapper functions.
