from msgspec import field

from ..base import BaseDatabaseReader


# @attrs.define
class SQLiteReader(BaseDatabaseReader, gc=False):
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

    type_: str = field(default="sqlite")
