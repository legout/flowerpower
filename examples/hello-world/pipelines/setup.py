import sys
import time
from pathlib import Path

import pandas as pd
from hamilton.function_modifiers import config, parameterize
from loguru import logger

from flowerpower.cfg import Config


@config.when(range=10_000)
def spend__10000() -> pd.Series:
    """Returns a series of spend data."""
    # time.sleep(2)
    return pd.Series(range(10_000)) * 10


@config.when(range=10_000)
def signups__10000() -> pd.Series:
    """Returns a series of signups data."""
    time.sleep(1)
    print(10_000)
    return pd.Series(range(10_000))


@config.when(range=1_000)
def spend__1000() -> pd.Series:
    """Returns a series of spend data."""
    # time.sleep(2)
    print(1_000)
    return pd.Series(range(10_000)) * 10


@config.when(range=1_000)
def signups__1000() -> pd.Series:
    """Returns a series of signups data."""
    time.sleep(1)
    print(1_000)
    return pd.Series(range(10_000))
