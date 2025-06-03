# FlowerPower pipeline test_mqtt.py
# Created on 2024-11-07 16:29:15


# from hamilton.function_modifiers import parameterize
import json
from pathlib import Path

import pandas as pd

from flowerpower.cfg import Config

PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="test_mqtt"
).pipeline.h_params


def df(payload: bytes) -> pd.DataFrame:
    data = json.loads(payload)
    return pd.DataFrame(data)


def print_df(df: pd.DataFrame) -> None:
    print(df)
