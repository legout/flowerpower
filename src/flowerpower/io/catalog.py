from ..config import load_catalog


CATALOG = load_catalog()


# Read from catalog
def load_table(table: str, namespace: str | None = None, path: str | None = None):
    global CATALOG
    if namespace is not None or path is not None:
        CATALOG = load_catalog(namspace=namespace, path=path)
    return CATALOG.load(table)


def write_table(
    data, table: str, namespace: str | None = None, path: str | None = None, **kwargs
):
    global CATALOG
    if namespace is not None or path is not None:
        CATALOG = load_catalog(namspace=namespace, path=path)

    CATALOG.write_table(data, table, **kwargs)


# Read from API


# Read from MQTT
