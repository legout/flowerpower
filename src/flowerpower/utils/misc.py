import os
import importlib

import tqdm
import tempfile
import subprocess
import time

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

    def _dict_to_dataframe(data: dict | list[dict]) -> pl.DataFrame | pa.Table:
        """
        Convert a dictionary or list of dictionaries to a polars DataFrame.

        Args:
            data: (dict | list[dict]) Data to convert.

        Returns:
            pl.DataFrame | pa.Table: Converted data.

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
                    return pl.DataFrame(data)
                # If values are scalars, convert list of dicts to DataFrame
                return pl.DataFrame(data)

        # If it's a single dict
        if isinstance(data, dict):
            # Check if values are lists/tuples
            if any(isinstance(v, (list, tuple)) for v in data.values()):
                # Get the length of any list value (assuming all lists have same length)
                length = len(
                    next(v for v in data.values() if isinstance(v, (list, tuple)))
                )
                # Convert to DataFrame where each list element becomes a row
                return pl.DataFrame(
                    {
                        k: v if isinstance(v, (list, tuple)) else [v] * length
                        for k, v in data.items()
                    }
                )
            # If values are scalars, wrap them in a list to create a single row
            return pl.DataFrame({k: [v] for k, v in data.items()})

        raise ValueError("Input must be a dictionary or list of dictionaries")

else:

    def _dict_to_dataframe(*args, **kwargs):
        raise ImportError("polars not installed")


if importlib.util.find_spec("joblib"):
    from joblib import Parallel, delayed

    def run_parallel(
        func: callable,
        func_params: list[any],
        *args,
        n_jobs: int = -1,
        backend: str = "threading",
        verbose: bool = True,
        **kwargs,
    ) -> list[any]:
        """Runs a function for a list of parameters in parallel.

        Args:
            func (Callable): function to run in Parallelallel.
            func_params (list[any]): parameters for the function
            n_jobs (int, optional): Number of joblib workers. Defaults to -1.
            backend (str, optional): joblib backend. Valid options are
            `loky`,`threading`, `mutliprocessing` or `sequential`.  Defaults to "threading".

        Returns:
            list[any]: Function output.
        """
        if not isinstance(func_params[0], list | tuple):
            func_params = [func_params]
        if verbose:
            return Parallel(n_jobs=n_jobs, backend=backend)(
                delayed(func)(*fp, *args, **kwargs)
                for fp in tqdm.tqdm(zip(*func_params))
            )

        else:
            return Parallel(n_jobs=n_jobs, backend=backend)(
                delayed(func)(*fp, *args, **kwargs) for fp in zip(*func_params)
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
