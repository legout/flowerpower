# FlowerPower pipeline basic_mqtt.py
# Created on 2025-05-21 13:30:33

####################################################################################################
# Import necessary libraries
# NOTE: Remove or comment out imports that are not used in the pipeline

from pathlib import Path

# from hamilton.function_modifiers import parameterize, dataloader, datasaver
# from hamilton.htypes import Parallelizable, Collect
import orjson
import polars as pl
from loguru import logger

from flowerpower.cfg import Config

####################################################################################################
# Load pipeline parameters. Do not modify this section.

PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="basic_mqtt"
).pipeline.h_params


####################################################################################################
# Helper functions.
# This functions have to start with an underscore (_).


####################################################################################################
# Pipeline functions


def data(payload: bytes, topic: str) -> dict:
    """Loads the payload from the MQTT message."""
    logger.info(f"Received message on topic {topic}")
    return orjson.loads(payload)


def to_df(data: dict) -> pl.DataFrame:
    """Converts the payload to a Polars DataFrame."""
    df = pl.DataFrame(data)
    return df


def print_df(to_df: pl.DataFrame) -> None:
    """Prints the DataFrame shape and head."""
    logger.info(f"Dataframe shape: {to_df.shape}")
    logger.info(f"Dataframe head:{to_df.head()}")
