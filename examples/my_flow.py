from flowerpower.config import load_params
from flowerpower.io.catalog import load_table, write_table
from hamilton.function_modifiers import parameterize
import polars as pl

PARAMS = load_params()


@parameterize(read_table=PARAMS.read_table.table_name)
def read(table_name: str) -> pl.DataFrame:
    return load_table(table_name).table.to_polars(lazy=False)


def append_col(
    read: pl.DataFrame,
) -> pl.DataFrame:
    return read.with_column(pl.col("a").abs().alias("abs_a"))


def write(append_col: pl.DataFrame, table_name: str) -> None:
    write_table(append_col, table_name)
