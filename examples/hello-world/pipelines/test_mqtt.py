# FlowerPower pipeline test_mqtt.py
# Created on 2024-11-07 16:29:15


from hamilton.function_modifiers import parameterize
import json
import pandas as pd
from flowerpower.cfg import Config
from pathlib import Path

PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="test_mqtt"
).pipeline.hamilton_func_params



def df(payload: bytes) -> pd.DataFrame:
    data = json.loads(payload)
    return pd.DataFrame(data)


def print_df(df: pd.DataFrame) -> None:
    print(df)

def to_lodl(df:pd.DataFrame, path:str, storage_options:dict)->None:
    write_deltalake(df, storage_options)
