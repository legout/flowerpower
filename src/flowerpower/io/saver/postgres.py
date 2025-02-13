from ..base import BaseDatabaseWriter


class PostgresWriter(BaseDatabaseWriter):
    """Postgres writer.

    This class is responsible for writing dataframes to Postgres database.

    Examples:
        ```python
        writer = PostgresWriter(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        writer.write(df)

        # or
        writer = PostgresWriter(table_name="table",
                                connection_string="postgresql://user:password@localhost:5432/database")
        writer.write(df)
        ```
    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.type_ = "postgres"
