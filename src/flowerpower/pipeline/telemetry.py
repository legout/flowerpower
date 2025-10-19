"""Telemetry and logging helpers for pipeline execution."""

from __future__ import annotations

from typing import Optional

from hamilton.registry import disable_autoload
from hamilton.telemetry import disable_telemetry

from .. import settings

_TELEMETRY_INITIALIZED = False


def initialize_telemetry(
    telemetry_enabled: Optional[bool] = None,
    autoload_enabled: Optional[bool] = None,
) -> None:
    """Configure Hamilton telemetry and autoload flags once per process."""
    global _TELEMETRY_INITIALIZED
    if _TELEMETRY_INITIALIZED:
        return

    telemetry = settings.HAMILTON_TELEMETRY_ENABLED if telemetry_enabled is None else telemetry_enabled
    autoload = settings.HAMILTON_AUTOLOAD_EXTENSIONS if autoload_enabled is None else autoload_enabled

    if not telemetry:
        disable_telemetry()
    if not autoload:
        disable_autoload()

    _TELEMETRY_INITIALIZED = True
