import attrs

from ..base import BaseDatabaseReader


@attrs.define
class DuckDBReader(BaseDatabaseReader):
    """DuckDB loader.

    This class is responsible for loading dataframes from DuckDB database.

    Examples:
        ```python
        loader = DuckDBReader(table_name="table", path="data.db")
        df = loader.to_polars("SELECT * FROM table WHERE column = 'value'")
        ```
    """

    type_: str = attrs.field(default="duckdb", init=False)
