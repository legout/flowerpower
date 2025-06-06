from msgspec import field

from ..base import BaseDatabaseWriter


# @attrs.define
class SQLiteWriter(BaseDatabaseWriter, gc=False):
    """SQLite writer.

    This class is responsible for writing dataframes to SQLite database.

    Examples:
        ```python
        writer = SQLiteWriter(table_name="table", path="data.db")
        writer.write(df)

        # or
        writer = SQLiteWriter(table_name="table",
                                connection_string="sqkite:///data.db")
        writer.write(df)
        ```
    """

    type_: str = field(default="sqlite")
