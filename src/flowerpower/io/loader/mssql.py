from ..base import BaseDatabaseLoader


class MSSQLLoader(BaseDatabaseLoader):
    """MSSQL loader.

    This class is responsible for loading dataframes from MSSQL database.

    Examples:
        ```python
        loader = MSSQLLoader(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        df = loader.to_polars()

        # or
        loader = MSSQLLoader(table_name="table",
                                connection_string="mssql+pyodbc://user:password@localhost:5432/database")
        df = loader.to_pyarrow_table("SELECT * FROM table WHERE column = 'value'")
        ```
    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.type_ = "mssql"
