import attrs

from ..base import BaseDatabaseWriter


@attrs.define
class DuckDBWriter(BaseDatabaseWriter):
    """DuckDB writer.

    This class is responsible for writing dataframes to DuckDB database.

    Examples:
        ```python
        writer = DuckDBWriter(table_name="table", path="data.db")
        writer.write(df)
        ```
    """

    type_: str = attrs.field(default="duckdb", init=False)
