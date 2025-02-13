from ..base import BaseDatabaseLoader


class SQLiteLoader(BaseDatabaseLoader):
    """SQLite loader.

    This class is responsible for loading dataframes from SQLite database.

    Examples:
        ```python
        loader = SQLiteLoader(table_name="table", path="data.db")
        df = loader.to_polars("SELECT * FROM table WHERE column = 'value'")

        # or
        loader = SQLiteLoader(table_name="table", connection_string="sqlite://data.db")
        df = loader.to_pyarrow_table()
        ```
    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.type_ = "sqlite"
