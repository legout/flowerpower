import attrs

from ..base import BaseDatabaseReader


@attrs.define
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

    type_: str = attrs.field(default="sqlite", init=False)
