from ..base import BaseDatabaseLoader


class DuckDBLoader(BaseDatabaseLoader):
    """DuckDB loader.

    This class is responsible for loading dataframes from DuckDB database.

    Examples:
        ```python
        loader = DuckDBLoader(table_name="table", path="data.db")
        df = loader.to_polars("SELECT * FROM table WHERE column = 'value'")
        ```
    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.type_ = "duckdb"
