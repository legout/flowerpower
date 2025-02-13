from ..base import BaseDatabaseWriter


class DuckDBWriter(BaseDatabaseWriter):
    """DuckDB writer.

    This class is responsible for writing dataframes to DuckDB database.

    Examples:
        ```python
        writer = DuckDBWriter(table_name="table", path="data.db")
        writer.write(df)
        ```
    """

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.type_ = "duckdb"
