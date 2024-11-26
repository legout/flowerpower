import orjson

import datafusion as dtf
import duckdb
import pandas as pd
import polars as pl
import pyarrow as pa
from hamilton.function_modifiers import dataloader
import datetime as dt
from typing import Any
from ..utils import get_dataframe_metadata


@dataloader()
def load_pandas_dataframe_from_mqtt(
    payload: bytes | dict[str, Any], topic: str | None = None
) -> tuple[pd.DataFrame, dict]:
    if isinstance(payload, bytes):
        payload = orjson.loads(payload)

    df = pd.DataFrame.from_dict(payload)
    metadata = get_dataframe_metadata(df, path=None, topic=topic, format="mqtt")
    return df, metadata


@dataloader()
def load_polars_dataframe_from_mqtt(
    payload: bytes | dict[str, Any], topic: str | None = None
) -> tuple[pl.DataFrame, dict]:
    if isinstance(payload, bytes):
        payload = orjson.loads(payload)

    df = pl.DataFrame(payload)
    metadata = get_dataframe_metadata(df, path=None, topic=topic, format="mqtt")

    return df, metadata


@dataloader()
def load_polars_lazyframe_from_mqtt(
    payload: bytes | dict[str, Any], topic: str | None = None
) -> tuple[pl.LazyFrame, dict]:
    if isinstance(payload, bytes):
        payload = orjson.loads(payload)

    df = pl.LazyFrame(payload)
    metadata = get_dataframe_metadata(df, path=None, topic=topic, format="mqtt")

    return df, metadata


@dataloader()
def load_pyarrow_table_from_mqtt(
    payload: bytes | dict[str, Any], topic: str | None = None
) -> tuple[pa.Table, dict]:
    if isinstance(payload, bytes):
        payload = orjson.loads(payload)

    table = pa.Table.from_pydict(payload)
    metadata = get_dataframe_metadata(table, path=None, topic=topic, format="mqtt")
    return table, metadata


@dataloader()
def load_duckdb_relation_from_mqtt(
    payload: bytes | dict[str, Any],
    topic: str | None = None,
    name: str | None = None,
    conn: duckdb.DuckDBPyConnection | None = None,
) -> tuple[duckdb.DuckDBPyRelation, dict]:
    table, metadata = load_pyarrow_table_from_mqtt(payload, topic=topic)
    if conn is None:
        conn = duckdb.connect()
    relation = conn.from_arrow(table)
    if name is not None:
        conn.register(name, relation)
    return relation, metadata


@dataloader()
def register_mqtt_in_duckdb(
    payload: bytes | dict[str, Any],
    topic: str | None = None,
    name: str | None = None,
    conn: duckdb.DuckDBPyConnection | None = None,
) -> tuple[duckdb.DuckDBPyConnection, dict]:
    table, metadata = load_pyarrow_table_from_mqtt(
        payload, topic=topic, name=name, conn=conn
    )
    if conn is None:
        conn = duckdb.connect()

    conn.register(name, table)
    return conn, metadata


@dataloader()
def register_mqtt_in_datafusion(
    payload: bytes | dict[str, Any],
    topic: str | None = None,
    name: str | None = None,
    conn: dtf.DataFrame | None = None,
) -> tuple[dtf.DataFrame, dict]:
    table, metadata = load_pyarrow_table_from_mqtt(
        payload, topic=topic, name=name, conn=conn
    )
    if conn is None:
        conn = dtf.DataFrame()
    conn.register(name, table)
    return conn, metadata
