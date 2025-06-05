import attrs

from ..base import BaseDatabaseWriter


@attrs.define
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

    type_: str = attrs.field(default="postgres", init=False)
