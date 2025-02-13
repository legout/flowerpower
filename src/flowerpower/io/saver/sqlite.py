from ..base import BaseDatabaseWriter


class SqliteWriter(BaseDatabaseWriter):
    """Sqlite writer.

    This class is responsible for writing dataframes to Sqlite database.

    Examples:
        ```python
        writer = SqliteWriter(table_name="table", path="data.db")
        writer.write(df)

        # or
        writer = SqliteWriter(table_name="table",
                                connection_string="sqkite:///data.db")
        writer.write(df)
        ```
    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.type_ = "sqlite"
