from ..base import BaseDatabaseReader


class DuckDBReader(BaseDatabaseReader):
    """DuckDB loader.

    This class is responsible for loading dataframes from DuckDB database.

    Examples:
        ```python
        loader = DuckDBReader(table_name="table", path="data.db")
        df = loader.to_polars("SELECT * FROM table WHERE column = 'value'")
        ```
    """

    type_: str = "duckdb"

    def model_post_init(self, __context):
        super().model_post_init(__context)
