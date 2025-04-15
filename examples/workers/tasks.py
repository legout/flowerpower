
from loguru import logger as logging
import time

def simple_task(message: str):
    """A simple task that logs a message."""
    logging.info(f"Executing task: {message}")
    time.sleep(2) # Simulate work
    result = f"Task completed: {message}"
    logging.info(result)
    return result