from ..base import BaseDatabaseWriter


class MSSQLWriter(BaseDatabaseWriter):
    """MSSQL writer.

    This class is responsible for writing dataframes to MsSQL database.

    Examples:
        ```python
        writer = MSSQLWriter(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        writer.write(df)

        # or
        writer = MSSQLWriter(table_name="table",
                                connection_string="mssql+pyodbc://user:password@localhost:5432/database")
        writer.write(df)
        ```
    """

    type_: str = "mssql"

    def model_post_init(self, __context):
        super().model_post_init(__context)
