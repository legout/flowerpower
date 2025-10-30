import importlib
import os
import subprocess
import tempfile
import time
# from collections.abc import Iterable
from typing import Any

import msgspec
from fsspeckit import AbstractFileSystem, filesystem
from .security import validate_file_path
from fsspeckit.utils import run_parallel

# if importlib.util.find_spec("joblib"):
#     from joblib import Parallel, delayed
#     from rich.progress import (BarColumn, Progress, TextColumn,
#                                TimeElapsedColumn)

#     def _prepare_parallel_args(
#         args: tuple, kwargs: dict
#     ) -> tuple[list, list, dict, dict, int]:
#         """Prepare and validate arguments for parallel execution.
        
#         Args:
#             args: Positional arguments
#             kwargs: Keyword arguments
            
#         Returns:
#             tuple: (iterables, fixed_args, iterable_kwargs, fixed_kwargs, first_iterable_len)
            
#         Raises:
#             ValueError: If no iterable arguments or length mismatch
#         """
#         iterables = []
#         fixed_args = []
#         iterable_kwargs = {}
#         fixed_kwargs = {}
#         first_iterable_len = None

#         # Process positional arguments
#         for arg in args:
#             if isinstance(arg, (list, tuple)) and not isinstance(arg[0], (list, tuple)):
#                 iterables.append(arg)
#                 if first_iterable_len is None:
#                     first_iterable_len = len(arg)
#                 elif len(arg) != first_iterable_len:
#                     raise ValueError(
#                         f"Iterable length mismatch: argument has length {len(arg)}, expected {first_iterable_len}"
#                     )
#             else:
#                 fixed_args.append(arg)

#         # Process keyword arguments
#         for key, value in kwargs.items():
#             if isinstance(value, (list, tuple)) and not isinstance(
#                 value[0], (list, tuple)
#             ):
#                 if first_iterable_len is None:
#                     first_iterable_len = len(value)
#                 elif len(value) != first_iterable_len:
#                     raise ValueError(
#                         f"Iterable length mismatch: {key} has length {len(value)}, expected {first_iterable_len}"
#                     )
#                 iterable_kwargs[key] = value
#             else:
#                 fixed_kwargs[key] = value

#         if first_iterable_len is None:
#             raise ValueError("At least one iterable argument is required")

#         return iterables, fixed_args, iterable_kwargs, fixed_kwargs, first_iterable_len

#     def _execute_parallel_with_progress(
#         func: callable,
#         iterables: list,
#         fixed_args: list,
#         iterable_kwargs: dict,
#         fixed_kwargs: dict,
#         param_combinations: list,
#         parallel_kwargs: dict,
#     ) -> list:
#         """Execute parallel tasks with progress tracking.
        
#         Args:
#             func: Function to execute
#             iterables: List of iterable arguments
#             fixed_args: List of fixed arguments
#             iterable_kwargs: Dictionary of iterable keyword arguments
#             fixed_kwargs: Dictionary of fixed keyword arguments
#             param_combinations: List of parameter combinations
#             parallel_kwargs: Parallel execution configuration
            
#         Returns:
#             list: Results from parallel execution
#         """
#         results = [None] * len(param_combinations)
#         with Progress(
#             TextColumn("[progress.description]{task.description}"),
#             BarColumn(),
#             "[progress.percentage]{task.percentage:>3.0f}%",
#             TimeElapsedColumn(),
#             transient=True,
#         ) as progress:
#             task = progress.add_task(
#                 "Running in parallel...", total=len(param_combinations)
#             )

#             def wrapper(idx, param_tuple):
#                 res = func(
#                     *(list(param_tuple[: len(iterables)]) + fixed_args),
#                     **{
#                         k: v
#                         for k, v in zip(
#                             iterable_kwargs.keys(), param_tuple[len(iterables) :]
#                         )
#                     },
#                     **fixed_kwargs,
#                 )
#                 progress.update(task, advance=1)
#                 return idx, res
#
#             for idx, result in Parallel(**parallel_kwargs)(
#                 delayed(wrapper)(i, param_tuple)
#                 for i, param_tuple in enumerate(param_combinations)
#             ):
#                 results[idx] = result
#         return results

#     def _execute_parallel_without_progress(
#         func: callable,
#         iterables: list,
#         fixed_args: list,
#         iterable_kwargs: dict,
#         fixed_kwargs: dict,
#         param_combinations: list,
#         parallel_kwargs: dict,
#     ) -> list:
#         """Execute parallel tasks without progress tracking.
        
#         Args:
#             func: Function to execute
#             iterables: List of iterable arguments
#             fixed_args: List of fixed arguments
#             iterable_kwargs: Dictionary of iterable keyword arguments
#             fixed_kwargs: Dictionary of fixed keyword arguments
#             param_combinations: List of parameter combinations
#             parallel_kwargs: Parallel execution configuration
            
#         Returns:
#             list: Results from parallel execution
#         """
#         return Parallel(**parallel_kwargs)(
#             delayed(func)(
#                 *(list(param_tuple[: len(iterables)]) + fixed_args),
#                 **{
#                     k: v
#                     for k, v in zip(
#                         iterable_kwargs.keys(), param_tuple[len(iterables) :]
#                     )
#                 },
#                 **fixed_kwargs,
#             )
#             for param_tuple in param_combinations
#         )

#     def run_parallel(
#         func: callable,
#         *args,
#         n_jobs: int = -1,
#         backend: str = "threading",
#         verbose: bool = True,
#         **kwargs,
#     ) -> list[any]:
#         """Runs a function for a list of parameters in parallel.

#         Args:
#             func (Callable): function to run in parallel
#             *args: Positional arguments. Can be single values or iterables
#             n_jobs (int, optional): Number of joblib workers. Defaults to -1
#             backend (str, optional): joblib backend. Valid options are
#                 `loky`,`threading`, `mutliprocessing` or `sequential`. Defaults to "threading"
#             verbose (bool, optional): Show progress bar. Defaults to True
#             **kwargs: Keyword arguments. Can be single values or iterables

#         Returns:
#             list[any]: Function output

#         Examples:
#             >>> # Single iterable argument
#             >>> run_parallel(func, [1,2,3], fixed_arg=42)

#             >>> # Multiple iterables in args and kwargs
#             >>> run_parallel(func, [1,2,3], val=[7,8,9], fixed=42)

#             >>> # Only kwargs iterables
#             >>> run_parallel(func, x=[1,2,3], y=[4,5,6], fixed=42)
#         """
#         parallel_kwargs = {"n_jobs": n_jobs, "backend": backend, "verbose": 0}

#         # Prepare and validate arguments
#         iterables, fixed_args, iterable_kwargs, fixed_kwargs, first_iterable_len = _prepare_parallel_args(
#             args, kwargs
#         )

#         # Create parameter combinations
#         all_iterables = iterables + list(iterable_kwargs.values())
#         param_combinations = list(zip(*all_iterables))

#         # Execute with or without progress tracking
#         if not verbose:
#             return _execute_parallel_without_progress(
#                 func, iterables, fixed_args, iterable_kwargs, fixed_kwargs,
#                 param_combinations, parallel_kwargs
#             )
#         else:
#             return _execute_parallel_with_progress(
#                 func, iterables, fixed_args, iterable_kwargs, fixed_kwargs,
#                 param_combinations, parallel_kwargs
#             )

# else:

#     def run_parallel(*args, **kwargs):
#         raise ImportError("joblib not installed")


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


def _validate_image_format(format: str) -> str:
    """Validate image format to prevent injection attacks.
    
    Args:
        format: Image format to validate
        
    Returns:
        str: Validated format
        
    Raises:
        ValueError: If format is not supported
    """
    allowed_formats = {"svg", "png", "jpg", "jpeg", "gif", "pdf", "html"}
    if format not in allowed_formats:
        raise ValueError(f"Unsupported format: {format}. Allowed: {allowed_formats}")
    return format

def _create_temp_image_file(data: str | bytes, format: str) -> str:
    """Create a temporary file with image data.
    
    Args:
        data: Image data as string or bytes
        format: Validated image format
        
    Returns:
        str: Path to temporary file
        
    Raises:
        OSError: If file creation fails
    """
    with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp:
        if isinstance(data, str):
            tmp.write(data.encode('utf-8'))
        else:
            tmp.write(data)
        tmp_path = tmp.name
    
    # Validate the temporary file path for security
    validate_file_path(tmp_path, allow_relative=False)
    return tmp_path

def _open_image_viewer(tmp_path: str) -> None:
    """Open image viewer with the given file path.
    
    Args:
        tmp_path: Path to temporary image file
        
    Raises:
        OSError: If platform is not supported
        subprocess.CalledProcessError: If subprocess fails
        subprocess.TimeoutExpired: If subprocess times out
    """
    import platform
    platform_system = platform.system()
    
    if platform_system == "Darwin":  # macOS
        subprocess.run(["open", tmp_path], check=True, timeout=10)
    elif platform_system == "Linux":
        subprocess.run(["xdg-open", tmp_path], check=True, timeout=10)
    elif platform_system == "Windows":
        subprocess.run(["start", "", tmp_path], shell=True, check=True, timeout=10)
    else:
        raise OSError(f"Unsupported platform: {platform_system}")

def _cleanup_temp_file(tmp_path: str) -> None:
    """Clean up temporary file.
    
    Args:
        tmp_path: Path to temporary file to remove
    """
    try:
        os.unlink(tmp_path)
    except OSError:
        pass  # File might already be deleted or in use

def view_img(data: str | bytes, format: str = "svg"):
    """View image data using the system's default image viewer.
    
    Args:
        data: Image data as string or bytes
        format: Image format (svg, png, jpg, jpeg, gif, pdf, html)
        
    Raises:
        ValueError: If format is not supported
        RuntimeError: If file opening fails
        OSError: If platform is not supported
    """
    # Validate format to prevent injection attacks
    validated_format = _validate_image_format(format)
    
    # Create a temporary file with validated extension
    tmp_path = _create_temp_image_file(data, validated_format)

    try:
        # Open image viewer with secure subprocess call
        _open_image_viewer(tmp_path)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as e:
        # Clean up temp file on error
        _cleanup_temp_file(tmp_path)
        raise RuntimeError(f"Failed to open file: {e}")

    # Optional: Remove the temp file after a delay
    time.sleep(2)  # Wait for viewer to open
    _cleanup_temp_file(tmp_path)


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
