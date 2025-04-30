from ..base import BaseDatabaseWriter


class PostgreSQLWriter(BaseDatabaseWriter):
    """PostgreSQL writer.

    This class is responsible for writing dataframes to PostgreSQL database.

    Examples:
        ```python
        writer = PostgreSQLWriter(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        writer.write(df)

        # or
        writer = PostgreSQLWriter(table_name="table",
                                connection_string="postgresql://user:password@localhost:5432/database")
        writer.write(df)
        ```
    """

    type_: str = "postgres"

    def model_post_init(self, __context):
        super().model_post_init(__context)
