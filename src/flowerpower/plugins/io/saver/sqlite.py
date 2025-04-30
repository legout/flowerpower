from ..base import BaseDatabaseWriter


class SQLiteWriter(BaseDatabaseWriter):
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

    type_: str = "sqlite"

    def model_post_init(self, __context):
        super().model_post_init(__context)
        # self.type_ = "sqlite"
