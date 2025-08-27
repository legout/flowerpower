import os
import sys

from loguru import logger

from ..settings import LOG_LEVEL


def setup_logging(level: str | None = None) -> None:
    """
    Configures the Loguru logger.

    Determines the logging level based on the following precedence:
    1. The 'level' argument passed to the function.
    2. The 'FP_LOG_LEVEL' environment variable.
    3. The 'LOG_LEVEL' from ..settings (which defaults to "CRITICAL").

    If the effective logging level is "CRITICAL", logging for the "flowerpower" module
    is disabled. Otherwise, logging is enabled and configured.
    """
    # Remove all existing handlers to prevent duplicate logs
    logger.remove()

    # Determine the effective logging level
    effective_level = level or os.getenv("FP_LOG_LEVEL") or LOG_LEVEL

    if effective_level.upper() == "CRITICAL":
        logger.disable("flowerpower")
    else:
        logger.enable("flowerpower")
        logger.add(
            sys.stderr,
            level=effective_level.upper(),
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )