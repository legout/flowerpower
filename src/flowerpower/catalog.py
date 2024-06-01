from pathlib import Path

from pydala.catalog import Catalog


def load_catalog(namespace: str | None = None, path: str | None = None) -> Catalog:
    """
    Load a catalog from a YAML file.

    Args:
        namespace (str | None, optional): The namespace of the catalog. Defaults to None.
        path (str | None, optional): The path to the YAML file. If not provided, the function will search
            for a file named "catalog*.y*ml" in the parent directories. Defaults to None.

    Returns:
        Catalog: The loaded catalog object.
    """
    if path is None:
        path = list(Path.cwd().rglob("catalog*.y*ml"))
        if not len(path):
            return
        path = path[0]

    return Catalog(path=path, namespace=namespace)


CATALOG = load_catalog()
