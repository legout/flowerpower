# This file makes the 'scheduler' directory a Python package.

from .factory import create_scheduler_adapter

__all__ = ["create_scheduler_adapter"]