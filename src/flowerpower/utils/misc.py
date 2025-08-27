import importlib
import os
import subprocess
import tempfile
import time
# from collections.abc import Iterable
from typing import Any

import msgspec
from fsspec_utils import AbstractFileSystem, filesystem

if importlib.util.find_spec("joblib"):
    from joblib import Parallel, delayed
    from rich.progress import (BarColumn, Progress, TextColumn,
                               TimeElapsedColumn)

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
        parallel_kwargs = {"n_jobs": n_jobs, "backend": backend, "verbose": 0}

        iterables = []
        fixed_args = []
        iterable_kwargs = {}
        fixed_kwargs = {}

        first_iterable_len = None

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

        all_iterables = iterables + list(iterable_kwargs.values())
        param_combinations = list(zip(*all_iterables))

        if not verbose:
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
            results = [None] * len(param_combinations)
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeElapsedColumn(),
                transient=True,
            ) as progress:
                task = progress.add_task(
                    "Running in parallel...", total=len(param_combinations)
                )

                def wrapper(idx, param_tuple):
                    res = func(
                        *(list(param_tuple[: len(iterables)]) + fixed_args),
                        **{
                            k: v
                            for k, v in zip(
                                iterable_kwargs.keys(), param_tuple[len(iterables) :]
                            )
                        },
                        **fixed_kwargs,
                    )
                    progress.update(task, advance=1)
                    return idx, res

                for idx, result in Parallel(**parallel_kwargs)(
                    delayed(wrapper)(i, param_tuple)
                    for i, param_tuple in enumerate(param_combinations)
                ):
                    results[idx] = result
            return results

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


def get_filesystem(fs: AbstractFileSystem | None = None, fs_type: str = "file") -> AbstractFileSystem:
    """
    Helper function to get a filesystem instance.
    
    Args:
        fs: An optional filesystem instance to use. If provided, this will be returned directly.
        fs_type: The type of filesystem to create if fs is None. Defaults to "file".
        
    Returns:
        An AbstractFileSystem instance.
    """
    if fs is None:
        fs = filesystem(fs_type)
    return fs
