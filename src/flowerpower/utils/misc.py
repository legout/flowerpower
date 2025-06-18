import importlib
import os
import subprocess
import tempfile
import time
# from collections.abc import Iterable
from typing import Any

import msgspec

if importlib.util.find_spec("pyarrow"):
    import pyarrow as pa

    def convert_large_types_to_standard(schema: pa.Schema) -> pa.Schema:
        # Define mapping of large types to standard types
        type_mapping = {
            pa.large_string(): pa.string(),
            pa.large_binary(): pa.binary(),
            pa.large_list(pa.null()): pa.list_(pa.null()),
        }

        # Convert fields
        new_fields = []
        for field in schema:
            field_type = field.type
            # Check if type exists in mapping
            if field_type in type_mapping:
                new_field = pa.field(
                    name=field.name,
                    type=type_mapping[field_type],
                    nullable=field.nullable,
                    metadata=field.metadata,
                )
                new_fields.append(new_field)
            # Handle large lists with nested types
            elif isinstance(field_type, pa.LargeListType):
                new_field = pa.field(
                    name=field.name,
                    type=pa.list_(field_type.value_type),
                    nullable=field.nullable,
                    metadata=field.metadata,
                )
                new_fields.append(new_field)
            else:
                new_fields.append(field)

        return pa.schema(new_fields)


else:

    def convert_large_types_to_standard(*args, **kwargs):
        raise ImportError("pyarrow not installed")


if importlib.util.find_spec("polars"):
    import polars as pl

    def _dict_to_dataframe(
        data: dict | list[dict], unique: bool | list[str] | str = False
    ) -> pl.DataFrame:
        """
        Convert a dictionary or list of dictionaries to a polars DataFrame.

        Args:
            data: (dict | list[dict]) Data to convert.

        Returns:
            pl.DataFrame: Converted data.

        Examples:
            >>> # Single dict with list values
            >>> data = {'a': [1, 2, 3], 'b': [4, 5, 6]}
            >>> _dict_to_dataframe(data)
            shape: (3, 2)
            ┌─────┬─────┐
            │ a   ┆ b   │
            │ --- ┆ --- │
            │ i64 ┆ i64 │
            ╞═════╪═════╡
            │ 1   ┆ 4   │
            │ 2   ┆ 5   │
            │ 3   ┆ 6   │
            └─────┴─────┘

            >>> # Single dict with scalar values
            >>> data = {'a': 1, 'b': 2}
            >>> _dict_to_dataframe(data)
            shape: (1, 2)
            ┌─────┬─────┐
            │ a   ┆ b   │
            │ --- ┆ --- │
            │ i64 ┆ i64 │
            ╞═════╪═════╡
            │ 1   ┆ 2   │
            └─────┴─────┘

            >>> # List of dicts with scalar values
            >>> data = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
            >>> _dict_to_dataframe(data)
            shape: (2, 2)
            ┌─────┬─────┐
            │ a   ┆ b   │
            │ --- ┆ --- │
            │ i64 ┆ i64 │
            ╞═════╪═════╡
            │ 1   ┆ 2   │
            │ 3   ┆ 4   │
            └─────┴─────┘

            >>> # List of dicts with list values
            >>> data = [{'a': [1, 2], 'b': [3, 4]}, {'a': [5, 6], 'b': [7, 8]}]
            >>> _dict_to_dataframe(data)
            shape: (2, 2)
            ┌───────┬───────┐
            │ a     ┆ b     │
            │ ---   ┆ ---   │
            │ list  ┆ list  │
            ╞═══════╪═══════╡
            │ [1,2] ┆ [3,4] │
            │ [5,6] ┆ [7,8] │
            └───────┴───────┘
        """
        if isinstance(data, list):
            # If it's a single-element list, just use the first element
            if len(data) == 1:
                data = data[0]
            # If it's a list of dicts
            else:
                first_item = data[0]
                # Check if the dict values are lists/tuples
                if any(isinstance(v, (list, tuple)) for v in first_item.values()):
                    # Each dict becomes a row with list/tuple values
                    data = pl.DataFrame(data)
                else:
                    # If values are scalars, convert list of dicts to DataFrame
                    data = pl.DataFrame(data)

                if unique:
                    data = data.unique(
                        subset=None if not isinstance(unique, str | list) else unique,
                        maintain_order=True,
                    )
                return data

        # If it's a single dict
        if isinstance(data, dict):
            # Check if values are lists/tuples
            if any(isinstance(v, (list, tuple)) for v in data.values()):
                # Get the length of any list value (assuming all lists have same length)
                length = len(
                    next(v for v in data.values() if isinstance(v, (list, tuple)))
                )
                # Convert to DataFrame where each list element becomes a row
                data = pl.DataFrame({
                    k: v if isinstance(v, (list, tuple)) else [v] * length
                    for k, v in data.items()
                })
            else:
                # If values are scalars, wrap them in a list to create a single row
                data = pl.DataFrame({k: [v] for k, v in data.items()})

            if unique:
                data = data.unique(
                    subset=None if not isinstance(unique, str | list) else unique,
                    maintain_order=True,
                )
            return data

        raise ValueError("Input must be a dictionary or list of dictionaries")

else:

    def _dict_to_dataframe(*args, **kwargs):
        raise ImportError("polars not installed")


if (
    importlib.util.find_spec("pandas")
    and importlib.util.find_spec("polars")
    and importlib.util.find_spec("pyarrow")
):
    from typing import Generator

    import pandas as pd

    def to_pyarrow_table(
        data: pl.DataFrame
        | pl.LazyFrame
        | pd.DataFrame
        | dict
        | list[pl.DataFrame | pl.LazyFrame | pd.DataFrame | dict],
        concat: bool = False,
        unique: bool | list[str] | str = False,
    ) -> pa.Table:
        if isinstance(data, dict):
            data = _dict_to_dataframe(data)
        if isinstance(data, list):
            if isinstance(data[0], dict):
                data = _dict_to_dataframe(data, unique=unique)

        if not isinstance(data, list):
            data = [data]

        if isinstance(data[0], pl.LazyFrame):
            data = [dd.collect() for dd in data]

        if isinstance(data[0], pl.DataFrame):
            if concat:
                data = pl.concat(data, how="diagonal_relaxed")
                if unique:
                    data = data.unique(
                        subset=None if not isinstance(unique, str | list) else unique,
                        maintain_order=True,
                    )
                data = data.to_arrow()
                data = data.cast(convert_large_types_to_standard(data.schema))
            else:
                data = [dd.to_arrow() for dd in data]
                data = [
                    dd.cast(convert_large_types_to_standard(dd.schema)) for dd in data
                ]

        elif isinstance(data[0], pd.DataFrame):
            data = [pa.Table.from_pandas(dd, preserve_index=False) for dd in data]
            if concat:
                data = pa.concat_tables(data, promote_options="permissive")
                if unique:
                    data = (
                        pl.from_arrow(data)
                        .unique(
                            subset=None
                            if not isinstance(unique, str | list)
                            else unique,
                            maintain_order=True,
                        )
                        .to_arrow()
                    )
                    data = data.cast(convert_large_types_to_standard(data.schema))

        elif isinstance(data[0], pa.RecordBatch | pa.RecordBatchReader | Generator):
            if concat:
                data = pa.Table.from_batches(data)
                if unique:
                    data = (
                        pl.from_arrow(data)
                        .unique(
                            subset=None
                            if not isinstance(unique, str | list)
                            else unique,
                            maintain_order=True,
                        )
                        .to_arrow()
                    )
                    data = data.cast(convert_large_types_to_standard(data.schema))
            else:
                data = [pa.Table.from_batches([dd]) for dd in data]

        return data

else:

    def to_pyarrow_table(*args, **kwargs):
        raise ImportError("pandas, polars, or pyarrow not installed")


if importlib.util.find_spec("joblib"):
    from joblib import Parallel, delayed

    def run_parallel(
        func: callable,
        *args,
        n_jobs: int = -1,
        backend: str = "threading",
        verbose: bool = True,
        **kwargs,
    ) -> list[any]:
        """Runs a function for a list of parameters in parallel.

        Args:
            func (Callable): function to run in parallel
            *args: Positional arguments. Can be single values or iterables
            n_jobs (int, optional): Number of joblib workers. Defaults to -1
            backend (str, optional): joblib backend. Valid options are
                `loky`,`threading`, `mutliprocessing` or `sequential`. Defaults to "threading"
            verbose (bool, optional): Show progress bar. Defaults to True
            **kwargs: Keyword arguments. Can be single values or iterables

        Returns:
            list[any]: Function output

        Examples:
            >>> # Single iterable argument
            >>> run_parallel(func, [1,2,3], fixed_arg=42)

            >>> # Multiple iterables in args and kwargs
            >>> run_parallel(func, [1,2,3], val=[7,8,9], fixed=42)

            >>> # Only kwargs iterables
            >>> run_parallel(func, x=[1,2,3], y=[4,5,6], fixed=42)
        """
        # Special kwargs for run_parallel itself
        parallel_kwargs = {"n_jobs": n_jobs, "backend": backend, "verbose": 0}

        # Process args and kwargs to separate iterables and fixed values
        iterables = []
        fixed_args = []
        iterable_kwargs = {}
        fixed_kwargs = {}

        # Get the length of the first iterable to determine number of iterations
        first_iterable_len = None

        # Process args
        for arg in args:
            if isinstance(arg, (list, tuple)) and not isinstance(arg[0], (list, tuple)):
                iterables.append(arg)
                if first_iterable_len is None:
                    first_iterable_len = len(arg)
                elif len(arg) != first_iterable_len:
                    raise ValueError(
                        f"Iterable length mismatch: argument has length {len(arg)}, expected {first_iterable_len}"
                    )
            else:
                fixed_args.append(arg)

        # Process kwargs
        for key, value in kwargs.items():
            if isinstance(value, (list, tuple)) and not isinstance(
                value[0], (list, tuple)
            ):
                if first_iterable_len is None:
                    first_iterable_len = len(value)
                elif len(value) != first_iterable_len:
                    raise ValueError(
                        f"Iterable length mismatch: {key} has length {len(value)}, expected {first_iterable_len}"
                    )
                iterable_kwargs[key] = value
            else:
                fixed_kwargs[key] = value

        if first_iterable_len is None:
            raise ValueError("At least one iterable argument is required")

        # Create parameter combinations
        all_iterables = iterables + list(iterable_kwargs.values())
        param_combinations = list(zip(*all_iterables))  # Convert to list for tqdm

        # if verbose:
        #    param_combinations = tqdm.tqdm(param_combinations)

        return Parallel(**parallel_kwargs)(
            delayed(func)(
                *(list(param_tuple[: len(iterables)]) + fixed_args),
                **{
                    k: v
                    for k, v in zip(
                        iterable_kwargs.keys(), param_tuple[len(iterables) :]
                    )
                },
                **fixed_kwargs,
            )
            for param_tuple in param_combinations
        )

else:

    def run_parallel(*args, **kwargs):
        raise ImportError("joblib not installed")


def get_partitions_from_path(
    path: str, partitioning: str | list[str] | None = None
) -> list[tuple]:
    """Get the dataset partitions from the file path.

    Args:
        path (str): File path.
        partitioning (str | list[str] | None, optional): Partitioning type. Defaults to None.

    Returns:
        list[tuple]: Partitions.
    """
    if "." in path:
        path = os.path.dirname(path)

    parts = path.split("/")

    if isinstance(partitioning, str):
        if partitioning == "hive":
            return [tuple(p.split("=")) for p in parts if "=" in p]

        else:
            return [
                (partitioning, parts[0]),
            ]
    else:
        return list(zip(partitioning, parts[-len(partitioning) :]))


def view_img(data: str | bytes, format: str = "svg"):
    # Create a temporary file with .svg extension
    with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    # Open with default application on macOS
    subprocess.run(["open", tmp_path])

    # Optional: Remove the temp file after a delay

    time.sleep(2)  # Wait for viewer to open
    os.unlink(tmp_path)


def update_config_from_dict(
    struct: msgspec.Struct, data: dict[str, Any]
) -> msgspec.Struct:
    """
    Updates a msgspec.Struct instance with values from a dictionary.
    Handles nested msgspec.Struct objects and nested dictionaries.

    Args:
        obj: The msgspec.Struct object to update
        update_dict: Dictionary containing update values

    Returns:
        Updated msgspec.Struct instance
    """
    # Convert the struct to a dictionary for easier manipulation
    obj_dict = msgspec.to_builtins(struct)

    # Update the dictionary recursively
    for key, value in data.items():
        if key in obj_dict:
            if isinstance(value, dict) and isinstance(obj_dict[key], dict):
                # Handle nested dictionaries
                obj_dict[key] = update_nested_dict(obj_dict[key], value)
            else:
                # Direct update for non-nested values
                obj_dict[key] = value

    # Convert back to the original struct type
    return msgspec.convert(obj_dict, type(struct))


def update_nested_dict(
    original: dict[str, Any], updates: dict[str, Any]
) -> dict[str, Any]:
    """Helper function to update nested dictionaries"""
    result = original.copy()
    for key, value in updates.items():
        if key in result and isinstance(value, dict) and isinstance(result[key], dict):
            # Recursively update nested dictionaries
            result[key] = update_nested_dict(result[key], value)
        else:
            # Direct update
            result[key] = value
    return result
