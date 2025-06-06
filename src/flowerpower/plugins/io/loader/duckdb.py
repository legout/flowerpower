from msgspec import field

from ..base import BaseDatabaseReader


# @attrs.define
class DuckDBReader(BaseDatabaseReader, gc=False):
    """DuckDB loader.

    This class is responsible for loading dataframes from DuckDB database.

    Examples:
        ```python
        loader = DuckDBReader(table_name="table", path="data.db")
        df = loader.to_polars("SELECT * FROM table WHERE column = 'value'")
        ```
    """

    type_: str = field(default="duckdb")
