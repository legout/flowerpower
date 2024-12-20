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
        if verbose:
            return Parallel(n_jobs=n_jobs, backend=backend)(
                delayed(func)(fp, *args, **kwargs) for fp in tqdm.tqdm(func_params)
            )

        else:
            return Parallel(n_jobs=n_jobs, backend=backend)(
                delayed(func)(fp, *args, **kwargs) for fp in func_params
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
