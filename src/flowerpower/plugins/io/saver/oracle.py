from msgspec import field

from ..base import BaseDatabaseWriter


# @attrs.define
class OracleDBWriter(BaseDatabaseWriter, gc=False):
    """OracleDB writer.

    This class is responsible for writing dataframes to OracleDB database.

    Examples:
        ```python
        writer = OracleDBWriter(table_name="table", host="localhost",
                                port=5432, username="user", password="password",
                                database="database")
        writer.write(df)

        # or
        writer = OracleDBWriter(table_name="table",
                                connection_string="mysql+pymsql://user:password@localhost:5432/database")
        writer.write(df)
        ```
    """

    type_: str = field(default="oracle")
