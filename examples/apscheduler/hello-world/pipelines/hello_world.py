# FlowerPower pipeline hello_world.py
# Created on 2024-10-26 12:44:27


import time
from pathlib import Path

import pandas as pd
from hamilton.function_modifiers import config, parameterize
from loguru import logger

from flowerpower.cfg import Config

PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="hello_world"
).pipeline.h_params


@config.when(range=10_000)
def spend__10000() -> pd.Series:
    """Returns a series of spend data."""
    # time.sleep(2)
    return pd.Series(range(10_000)) * 10


@config.when(range=10_000)
def signups__10000() -> pd.Series:
    """Returns a series of signups data."""
    time.sleep(1)
    return pd.Series(range(10_000))


@config.when(range=1_000)
def spend__1000() -> pd.Series:
    """Returns a series of spend data."""
    # time.sleep(2)
    return pd.Series(range(10_000)) * 10


@config.when(range=1_000)
def signups__1000() -> pd.Series:
    """Returns a series of signups data."""
    time.sleep(1)
    return pd.Series(range(10_000))


@parameterize(
    **PARAMS.avg_x_wk_spend
)  # (**{"avg_x_wk_spend": {"rolling": value(3)}})  #
def avg_x_wk_spend(spend: pd.Series, rolling: int) -> pd.Series:
    """Rolling x week average spend."""
    # time.sleep(2)
    return spend.rolling(rolling).mean()


def spend_per_signup(spend: pd.Series, signups: pd.Series) -> pd.Series:
    """The cost per signup in relation to spend."""
    time.sleep(1)
    return spend / signups


def spend_mean(spend: pd.Series) -> float:
    """Shows function creating a scalar. In this case it computes the mean of the entire column."""
    return spend.mean()


@parameterize(
    **PARAMS.spend_zero_mean
)  # (**{"spend_zero_mean": {"offset": value(0)}})  #
def spend_zero_mean(spend: pd.Series, spend_mean: float, offset: int) -> pd.Series:
    """Shows function that takes a scalar. In this case to zero mean spend."""
    return spend - spend_mean + offset


def spend_std_dev(spend: pd.Series) -> float:
    """Function that computes the standard deviation of the spend column."""
    return spend.std()


def spend_zero_mean_unit_variance(
    spend_zero_mean: pd.Series, spend_std_dev: float, verbose: bool = False
) -> pd.Series:
    """Function showing one way to make spend have zero mean and unit variance."""
    if verbose:
        logger.info(f"spend_zero_mean_unit_variance {spend_zero_mean / spend_std_dev}")
    return spend_zero_mean / spend_std_dev
