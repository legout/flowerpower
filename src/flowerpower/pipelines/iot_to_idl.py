import datetime as dt
from pathlib import Path
import numpy as np
import pandas as pd
from fsspec import AbstractFileSystem
from hamilton.function_modifiers import parameterize, source, value
from mindsphere_tools.iot_timeseries import Client
from pydala.dataset import ParquetDataset

from ..helpers import filesystem as filesystem_, iot_client as iot_client_
from ..config import load_params


PARAMS = load_params(ht_values=True).pipelines[Path(__file__).stem]


def start_date() -> dt.datetime:
    return dt.datetime.now() + dt.timedelta(days=-30)


def end_date() -> dt.datetime:
    return dt.datetime.now()


# @parameterize(filesystem=PARAMS.filesystem)
def filesystem(filesystem_params: dict) -> AbstractFileSystem:
    return filesystem_(**filesystem_params)


def iot_client() -> Client:
    return iot_client_()


@parameterize(
    df_raw1=PARAMS.df_raw1,
    df_raw2=PARAMS.df_raw2,
)
# @extract_columns("Prozessergebnis", "Serialnummer_Motor")
def df_raw(
    start_date: dt.datetime,
    end_date: dt.datetime,
    asset_id: dt.datetime,
    aspect: str,
    iot_client: Client,
) -> pd.DataFrame:
    df = iot_client.download(
        from_date=start_date,
        to_date=end_date,
        asset_id=asset_id,
        aspect=aspect,
    )

    return df


@parameterize(
    df_dropna1=dict(df_raw=source("df_raw1")),
    df_dropna2=dict(df_raw=source("df_raw2")),
)
def df_dropna(df_raw: pd.DataFrame) -> pd.DataFrame:
    df_dropna = (
        df_raw.replace(" ", np.nan)
        .dropna()
        .reset_index()[["Prozessergebnis", "Serialnummer_Motor", "_time"]]
    )
    return df_dropna


@parameterize(
    df_renamed_cols1=dict(
        df_dropna=source("df_dropna1"),
        rename_columns=value(
            dict(
                Prozessergebnis="Ergebnis_Zelle2",
            )
        ),
    ),
    df_renamed_cols2=dict(
        df_dropna=source("df_dropna2"),
        rename_columns=value(
            dict(
                Prozessergebnis="Ergebnis_Zelle3",
            )
        ),
    ),
)
def df_renamed_cols(
    df_dropna: pd.DataFrame, rename_columns: dict[str, str]
) -> pd.DataFrame:
    df_renamed_cols = df_dropna.rename(columns=rename_columns)
    return df_renamed_cols


# @parameterize(
#    df_merged=dict(
#        df_renamed_cols1=source("df_renamed_cols1"),
#        df_renamed_cols2=source("df_renamed_cols2"),
#    )
# )
def df_merged(
    df_renamed_cols1: pd.DataFrame,
    df_renamed_cols2: pd.DataFrame,
    on_: str,
    how: str,
) -> pd.DataFrame:
    df_merged = pd.merge(
        df_renamed_cols1,
        df_renamed_cols2,
        on=on_,
        how=how,
        suffixes=["_temp", ""],
    ).drop("_time_temp", axis=1)

    return df_merged


def df_time2str(df_merged: pd.DataFrame) -> pd.DataFrame:
    df_merged["_time"] = pd.to_datetime(
        df_merged["_time"].str[:19].str.replace("T", " ")
    )
    return df_merged


# @parameterize(to_idl=PARAMS.to_idl)
def to_idl(
    df_time2str: pd.DataFrame,
    path: str,
    filesystem: AbstractFileSystem,
) -> None:
    ds = ParquetDataset(path=path, filesystem=filesystem)
    ds.write_to_dataset(df=df_time2str, mode="delta")

    return ds
