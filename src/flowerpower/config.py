import yaml
from pydala.catalog import Catalog
from munch import Munch, munchify
from pathlib import Path
from hamilton.function_modifiers import value


def load_pipeline_params(path: str | None = None, ht_values: bool = False) -> Munch:
    """
    Load parameters from a YAML file.

    Args:
        path (str | None, optional): The path to the YAML file. If None, the function will
            search for a file named "param*.y*ml" in the parent directories. Defaults to None.
        ht_values (bool, optional): Whether to convert the loaded parameters to high-throughput (HT) values.
            Defaults to False.

    Returns:
        Munch: A Munch object containing the loaded parameters.
    """

    if path is None:
        path = list(Path(__file__).parents[2].rglob("pipeline*.y*ml"))
        if not len(path):
            return
        path = path[0]

    with open(path) as f:
        params = yaml.full_load(f)

    if ht_values:
        params = _to_ht_value(params)

    return munchify(params)


def _to_ht_value(value_dict: dict) -> dict:
    """
    Recursively converts the values in a dictionary to a specific format.

    Args:
        value_dict (dict): The dictionary containing the values to be converted.

    Returns:
        dict: The dictionary with the converted values.

    """
    if isinstance(value_dict, dict):
        return {k: _to_ht_value(v) for k, v in value_dict.items()}
    else:
        return value(value_dict)


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
        path = list(Path(__file__).parents[2].rglob("catalog*.y*ml"))
        if not len(path):
            return
        path = path[0]

    return Catalog(path=path, namespace=namespace)


def load_scheduler_params(
    path: str | None = None,
) -> Munch:
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
        path = list(Path(__file__).parents[2].rglob("scheduler*.y*ml"))
        if not len(path):
            return
        path = path[0]

    with open(path) as f:
        params = yaml.full_load(f)

    return munchify(params)
