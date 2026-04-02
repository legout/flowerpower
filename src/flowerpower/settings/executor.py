import os


def _safe_cpu_count(default: int = 2) -> int:
    """Return os.cpu_count() safely, with a fallback default if None.

    Args:
        default: Value to return if os.cpu_count() returns None.

    Returns:
        Actual CPU count or the default value.
    """
    return os.cpu_count() or default


def _env_bool(value: str | None, default: bool = False) -> bool:
    """Parse an environment variable value as a boolean.

    Handles common false representations like "False", "false", "0", "no", "n".

    Args:
        value: The environment variable value (or None if not set).
        default: Default boolean value if value is None.

    Returns:
        True or False based on the parsed value.
    """
    if value is None:
        return default
    return value.strip().lower() not in ("false", "0", "no", "n", "", "off")


# EXECUTOR
EXECUTOR = os.getenv("FP_EXECUTOR", "threadpool")
EXECUTOR_MAX_WORKERS = int(
    os.getenv("FP_EXECUTOR_MAX_WORKERS", _safe_cpu_count(2) * 5)
)
EXECUTOR_NUM_CPUS = int(os.getenv("FP_EXECUTOR_NUM_CPUS", _safe_cpu_count(1)))
