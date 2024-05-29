from ..config import load_catalog
from pydala.dataset import ParquetDataset, CsvDataset, JsonDataset, PyarrowDataset

CATALOG = load_catalog()


# Read from catalog
def load_table(
    table: str, namespace: str | None = None, path: str | None = None
) -> ParquetDataset | CsvDataset | JsonDataset | PyarrowDataset:
    global CATALOG
    if CATALOG is None:
        CATALOG = load_catalog(namspace=namespace, path=path)
    return CATALOG.load(table)


def write_table(
    data, table: str, namespace: str | None = None, path: str | None = None, **kwargs
):
    global CATALOG
    if CATALOG is None:
        CATALOG = load_catalog(namspace=namespace, path=path)

    CATALOG.write_table(data, table, **kwargs)
