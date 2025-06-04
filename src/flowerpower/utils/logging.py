import sys

from loguru import logger

from ..settings import LOG_LEVEL  # Import the setting


def setup_logging(level: str = LOG_LEVEL, disable: bool = False) -> None:
    """
    Configures the Loguru logger.

    Removes the default handler and adds a new one targeting stderr
    with the level specified by the FP_LOG_LEVEL setting.
    """
    logger.remove()  # Remove the default handler added by Loguru
    logger.add(
        sys.stderr,
        level=level.upper(),  # Use the level from the parameter, ensure it's uppercase
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",  # Example format
    )
    if disable:
        logger.disable("flowerpower")
    # logger.info(f"Log level set to: {FP_LOG_LEVEL.upper()}")
