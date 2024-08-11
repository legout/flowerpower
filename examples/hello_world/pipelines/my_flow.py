import pandas as pd
from hamilton.function_modifiers import parameterize
from flowerpower.cfg import Config
from pathlib import Path

PARAMS = Config(path=Path(__file__).parents[1] / "conf").pipeline_params.my_flow


def spend() -> pd.Series:
    """Returns a series of spend data."""
    return pd.Series([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])


def signups() -> pd.Series:
    """Returns a series of signups data."""
    return pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])


@parameterize(**PARAMS.avg_x_wk_spend)
def avg_x_wk_spend(spend: pd.Series, rolling: int) -> pd.Series:
    """Rolling x week average spend."""
    return spend.rolling(rolling).mean()


def spend_per_signup(spend: pd.Series, signups: pd.Series) -> pd.Series:
    """The cost per signup in relation to spend."""
    return spend / signups


def spend_mean(spend: pd.Series) -> float:
    """Shows function creating a scalar. In this case it computes the mean of the entire column."""
    return spend.mean()


@parameterize(**PARAMS.spend_zero_mean)
def spend_zero_mean(spend: pd.Series, spend_mean: float, offset: int) -> pd.Series:
    """Shows function that takes a scalar. In this case to zero mean spend."""
    return spend - spend_mean + offset


def spend_std_dev(spend: pd.Series) -> float:
    """Function that computes the standard deviation of the spend column."""
    return spend.std()


def spend_zero_mean_unit_variance(
    spend_zero_mean: pd.Series, spend_std_dev: float
) -> pd.Series:
    """Function showing one way to make spend have zero mean and unit variance."""
    return spend_zero_mean / spend_std_dev
