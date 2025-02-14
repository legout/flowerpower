from ..base import BaseDatabaseReader


class SQLiteReader(BaseDatabaseReader):
    """SQLite loader.

    This class is responsible for loading dataframes from SQLite database.

    Examples:
        ```python
        loader = SQLiteReader(table_name="table", path="data.db")
        df = loader.to_polars("SELECT * FROM table WHERE column = 'value'")

        # or
        loader = SQLiteReader(table_name="table", connection_string="sqlite://data.db")
        df = loader.to_pyarrow_table()
        ```
    """

    type_: str = "sqlite"

    def model_post_init(self, __context):
        super().model_post_init(__context)
