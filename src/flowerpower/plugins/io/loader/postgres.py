from msgspec import field

from ..base import BaseDatabaseReader


# @attrs.define
class PostgreSQLReader(BaseDatabaseReader, gc=False):
    """PostgreSQL loader.

    This class is responsible for loading dataframes from PostgreSQL database.

    Examples:
        ```python
        loader = PostgreSQLReader(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        df = loader.to_polars()

        # or
        loader = PostgreSQLReader(table_name="table",
                                connection_string="mssql+pyodbc://user:password@localhost:5432/database")
        df = loader.to_pyarrow_table("SELECT * FROM table WHERE column = 'value'")
        ```
    """

    type_: str = field(default="postgres")
