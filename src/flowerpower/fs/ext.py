import datetime as dt
import importlib
import posixpath
import uuid
from typing import Any, Generator

if importlib.util.find_spec("pandas") is not None:
    import pandas as pd
else:
    raise ImportError("To use this module, please install `flowerpower[io]`.")

import orjson
# import polars as pl
import pyarrow as pa
import pyarrow.dataset as pds
import pyarrow.parquet as pq
from fsspec import AbstractFileSystem
from pydala.dataset import ParquetDataset

from ..plugins.io.helpers.polars import opt_dtype as opt_dtype_pl
from ..plugins.io.helpers.polars import pl
# from ..plugins.io.helpers.polars import unify_schemas as unfify_schemas_pl
from ..plugins.io.helpers.pyarrow import cast_schema
from ..plugins.io.helpers.pyarrow import opt_dtype as opt_dtype_pa
from ..plugins.io.helpers.pyarrow import unify_schemas as unify_schemas_pa
from ..utils.misc import (_dict_to_dataframe, convert_large_types_to_standard,
                          run_parallel, to_pyarrow_table)


def path_to_glob(path: str, format: str | None = None) -> str:
    """Convert a path to a glob pattern for file matching.

    Intelligently converts paths to glob patterns that match files of the specified
    format, handling various directory and wildcard patterns.

    Args:
        path: Base path to convert. Can include wildcards (* or **).
            Examples: "data/", "data/*.json", "data/**"
        format: File format to match (without dot). If None, inferred from path.
            Examples: "json", "csv", "parquet"

    Returns:
        str: Glob pattern that matches files of specified format.
            Examples: "data/**/*.json", "data/*.csv"

    Example:
        >>> # Basic directory
        >>> path_to_glob("data", "json")
        'data/**/*.json'
        >>>
        >>> # With wildcards
        >>> path_to_glob("data/**", "csv")
        'data/**/*.csv'
        >>>
        >>> # Format inference
        >>> path_to_glob("data/file.parquet")
        'data/file.parquet'
    """
    path = path.rstrip("/")
    if format is None:
        if ".json" in path:
            format = "json"
        elif ".csv" in path:
            format = "csv"
        elif ".parquet" in path:
            format = "parquet"

    if format in path:
        return path
    else:
        if path.endswith("**"):
            return posixpath.join(path, f"*.{format}")
        elif path.endswith("*"):
            if path.endswith("*/*"):
                return path + f".{format}"
            return posixpath.join(path.rstrip("/*"), f"*.{format}")
        return posixpath.join(path, f"**/*.{format}")


def _read_json_file(
    path: str,
    self: AbstractFileSystem,
    include_file_path: bool = False,
    jsonlines: bool = False,
) -> dict | list[dict]:
    """Read a JSON file from any filesystem.

    Internal function that handles both regular JSON and JSON Lines formats.

    Args:
        path: Path to JSON file
        self: Filesystem instance to use for reading
        include_file_path: Whether to return dict with filepath as key
        jsonlines: Whether to read as JSON Lines format

    Returns:
        dict | list[dict]: Parsed JSON data. If include_file_path=True,
            returns {filepath: data}

    Example:
        >>> fs = LocalFileSystem()
        >>> # Regular JSON
        >>> data = _read_json_file("data.json", fs)
        >>> print(type(data))
        <class 'dict'>
        >>>
        >>> # JSON Lines with filepath
        >>> data = _read_json_file(
        ...     "data.jsonl",
        ...     fs,
        ...     include_file_path=True,
        ...     jsonlines=True
        ... )
        >>> print(list(data.keys())[0])
        'data.jsonl'
    """
    with self.open(path) as f:
        if jsonlines:
            data = [orjson.loads(line) for line in f.readlines()]
        else:
            data = orjson.loads(f.read())
    if include_file_path:
        return {path: data}
    return data


def read_json_file(
    self: AbstractFileSystem,
    path: str,
    include_file_path: bool = False,
    jsonlines: bool = False,
) -> dict | list[dict]:
    """Read a single JSON file from any filesystem.

    A public wrapper around _read_json_file providing a clean interface for
    reading individual JSON files.

    Args:
        path: Path to JSON file to read
        include_file_path: Whether to return dict with filepath as key
        jsonlines: Whether to read as JSON Lines format

    Returns:
        dict | list[dict]: Parsed JSON data. For regular JSON, returns a dict.
            For JSON Lines, returns a list of dicts. If include_file_path=True,
            returns {filepath: data}.

    Example:
        >>> fs = LocalFileSystem()
        >>> # Read regular JSON
        >>> data = fs.read_json_file("config.json")
        >>> print(data["setting"])
        'value'
        >>>
        >>> # Read JSON Lines with filepath
        >>> data = fs.read_json_file(
        ...     "logs.jsonl",
        ...     include_file_path=True,
        ...     jsonlines=True
        ... )
        >>> print(list(data.keys())[0])
        'logs.jsonl'
    """
    return _read_json_file(
        path=path,
        self=self,
        include_file_path=include_file_path,
        jsonlines=jsonlines,
    )


def _read_json(
    self,
    path: str | list[str],
    include_file_path: bool = False,
    use_threads: bool = True,
    jsonlines: bool = False,
    as_dataframe: bool = True,
    concat: bool = True,
    verbose: bool = False,
    opt_dtypes: bool = False,
    **kwargs,
) -> dict | list[dict] | pl.DataFrame | list[pl.DataFrame]:
    """
    Read a JSON file or a list of JSON files.

    Args:
        path: (str | list[str]) Path to the JSON file(s).
        include_file_path: (bool, optional) If True, return a dictionary with the file path as key.
            Defaults to False.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        jsonlines: (bool, optional) If True, read JSON lines. Defaults to False.
        as_dataframe: (bool, optional) If True, return a DataFrame. Defaults to True.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        opt_dtypes: (bool, optional) If True, optimize DataFrame dtypes. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        (dict | list[dict] | pl.DataFrame | list[pl.DataFrame]):
            Dictionary, list of dictionaries, DataFrame or list of DataFrames.
    """
    if isinstance(path, str):
        path = path_to_glob(path, format="json")
        path = self.glob(path)

    if isinstance(path, list):
        if use_threads:
            data = run_parallel(
                _read_json_file,
                path,
                self=self,
                include_file_path=include_file_path,
                jsonlines=jsonlines,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        data = [
            _read_json_file(
                path=p,
                self=self,
                include_file_path=include_file_path,
                jsonlines=jsonlines,
            )
            for p in path
        ]
    else:
        data = _read_json_file(
            path=path,
            self=self,
            include_file_path=include_file_path,
            jsonlines=jsonlines,
        )
    if as_dataframe:
        if not include_file_path:
            data = [pl.DataFrame(d) for d in data]
        else:
            data = [
                [
                    pl.DataFrame(_data[k]).with_columns(pl.lit(k).alias("file_path"))
                    for k in _data
                ][0]
                for _data in data
            ]
        if opt_dtypes:
            data = [opt_dtype_pl(df, strict=False) for df in data]
        if concat:
            result = pl.concat(data, how="diagonal_relaxed")
            # if opt_dtypes:
            #   result = opt_dtype_pl(result, strict=False)
            return result
    return data


def _read_json_batches(
    self: AbstractFileSystem,
    path: str | list[str],
    batch_size: int | None = None,
    include_file_path: bool = False,
    jsonlines: bool = False,
    as_dataframe: bool = True,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    opt_dtypes: bool = False,
    **kwargs: Any,
) -> Generator[dict | list[dict] | pl.DataFrame | list[pl.DataFrame], None, None]:
    """Process JSON files in batches with optional parallel reading.

    Internal generator function that handles batched reading of JSON files
    with support for parallel processing within each batch.

    Args:
        path: Path(s) to JSON file(s). Glob patterns supported.
        batch_size: Number of files to process in each batch
        include_file_path: Include source filepath in output
        jsonlines: Whether to read as JSON Lines format
        as_dataframe: Convert output to Polars DataFrame(s)
        concat: Combine files within each batch
        use_threads: Enable parallel file reading within batches
        verbose: Print progress information
        opt_dtypes: Optimize DataFrame dtypes
        **kwargs: Additional arguments for DataFrame conversion

    Yields:
        Each batch of data in requested format:
        - dict | list[dict]: Raw JSON data
        - pl.DataFrame: Single DataFrame if concat=True
        - list[pl.DataFrame]: List of DataFrames if concat=False

    Example:
        >>> fs = LocalFileSystem()
        >>> # Process large dataset in batches
        >>> for batch in fs._read_json_batches(
        ...     "data/*.json",
        ...     batch_size=100,
        ...     as_dataframe=True,
        ...     verbose=True
        ... ):
        ...     print(f"Batch shape: {batch.shape}")
        >>>
        >>> # Parallel batch processing with filepath tracking
        >>> for batch in fs._read_json_batches(
        ...     ["logs1.jsonl", "logs2.jsonl"],
        ...     batch_size=1,
        ...     include_file_path=True,
        ...     use_threads=True
        ... ):
        ...     print(f"Processing {batch['file_path'][0]}")
    """
    # Handle path resolution
    if isinstance(path, str):
        path = path_to_glob(path, format="json")
        path = self.glob(path)

    # Process files in batches
    for i in range(0, len(path), batch_size):
        batch_paths = path[i : i + batch_size]

        # Read batch with optional parallelization
        if use_threads and len(batch_paths) > 1:
            batch_data = run_parallel(
                _read_json_file,
                batch_paths,
                self=self,
                include_file_path=include_file_path,
                jsonlines=jsonlines,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        else:
            batch_data = [
                _read_json_file(
                    path=p,
                    self=self,
                    include_file_path=include_file_path,
                    jsonlines=jsonlines,
                )
                for p in batch_paths
            ]

        if as_dataframe:
            if not include_file_path:
                batch_dfs = [pl.DataFrame(d) for d in batch_data]
            else:
                batch_dfs = [
                    [
                        pl.DataFrame(_data[k]).with_columns(
                            pl.lit(k).alias("file_path")
                        )
                        for k in _data
                    ][0]
                    for _data in batch_data
                ]
            if opt_dtypes:
                batch_dfs = [opt_dtype_pl(df, strict=False) for df in batch_dfs]
            if concat and len(batch_dfs) > 1:
                batch_df = pl.concat(batch_dfs, how="diagonal_relaxed")
                # if opt_dtypes:
                #    batch_df = opt_dtype_pl(batch_df, strict=False)
                yield batch_df
            else:
                # if opt_dtypes:
                #    batch_dfs = [opt_dtype_pl(df, strict=False) for df in batch_dfs]
                yield batch_dfs
        else:
            yield batch_data


def read_json(
    self: AbstractFileSystem,
    path: str | list[str],
    batch_size: int | None = None,
    include_file_path: bool = False,
    jsonlines: bool = False,
    as_dataframe: bool = True,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    opt_dtypes: bool = False,
    **kwargs: Any,
) -> (
    dict
    | list[dict]
    | pl.DataFrame
    | list[pl.DataFrame]
    | Generator[dict | list[dict] | pl.DataFrame | list[pl.DataFrame], None, None]
):
    """Read JSON data from one or more files with powerful options.

    Provides a flexible interface for reading JSON data with support for:
    - Single file or multiple files
    - Regular JSON or JSON Lines format
    - Batch processing for large datasets
    - Parallel processing
    - DataFrame conversion
    - File path tracking

    Args:
        path: Path(s) to JSON file(s). Can be:
            - Single path string (globs supported)
            - List of path strings
        batch_size: If set, enables batch reading with this many files per batch
        include_file_path: Include source filepath in output
        jsonlines: Whether to read as JSON Lines format
        as_dataframe: Convert output to Polars DataFrame(s)
        concat: Combine multiple files/batches into single result
        use_threads: Enable parallel file reading
        verbose: Print progress information
        opt_dtypes: Optimize DataFrame dtypes for performance
        **kwargs: Additional arguments passed to DataFrame conversion

    Returns:
        Various types depending on arguments:
        - dict: Single JSON file as dictionary
        - list[dict]: Multiple JSON files as list of dictionaries
        - pl.DataFrame: Single or concatenated DataFrame
        - list[pl.DataFrame]: List of DataFrames (if concat=False)
        - Generator: If batch_size set, yields batches of above types

    Example:
        >>> fs = LocalFileSystem()
        >>> # Read all JSON files in directory
        >>> df = fs.read_json(
        ...     "data/*.json",
        ...     as_dataframe=True,
        ...     concat=True
        ... )
        >>> print(df.shape)
        (1000, 5)  # Combined data from all files
        >>>
        >>> # Batch process large dataset
        >>> for batch_df in fs.read_json(
        ...     "logs/*.jsonl",
        ...     batch_size=100,
        ...     jsonlines=True,
        ...     include_file_path=True
        ... ):
        ...     print(f"Processing {len(batch_df)} records")
        >>>
        >>> # Parallel read with custom options
        >>> dfs = fs.read_json(
        ...     ["file1.json", "file2.json"],
        ...     use_threads=True,
        ...     concat=False,
        ...     verbose=True
        ... )
        >>> print(f"Read {len(dfs)} files")
    """
    if batch_size is not None:
        return _read_json_batches(
            self=self,
            path=path,
            batch_size=batch_size,
            include_file_path=include_file_path,
            jsonlines=jsonlines,
            as_dataframe=as_dataframe,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
    return _read_json(
        self=self,
        path=path,
        include_file_path=include_file_path,
        jsonlines=jsonlines,
        as_dataframe=as_dataframe,
        concat=concat,
        use_threads=use_threads,
        verbose=verbose,
        opt_dtypes=opt_dtypes,
        **kwargs,
    )


def _read_csv_file(
    path: str,
    self: AbstractFileSystem,
    include_file_path: bool = False,
    opt_dtypes: bool = False,
    **kwargs: Any,
) -> pl.DataFrame:
    """Read a single CSV file from any filesystem.

    Internal function that handles reading individual CSV files and optionally
    adds the source filepath as a column.

    Args:
        path: Path to CSV file
        self: Filesystem instance to use for reading
        include_file_path: Add source filepath as a column
        opt_dtypes: Optimize DataFrame dtypes
        **kwargs: Additional arguments passed to pl.read_csv()

    Returns:
        pl.DataFrame: DataFrame containing CSV data

    Example:
        >>> fs = LocalFileSystem()
        >>> df = _read_csv_file(
        ...     "data.csv",
        ...     fs,
        ...     include_file_path=True,
        ...     delimiter="|"
        ... )
        >>> print("file_path" in df.columns)
        True
    """
    print(path)  # Debug info
    with self.open(path) as f:
        df = pl.read_csv(f, **kwargs)
    if include_file_path:
        df = df.with_columns(pl.lit(path).alias("file_path"))
    if opt_dtypes:
        df = opt_dtype_pl(df, strict=False)
    return df


def read_csv_file(
    self, path: str, include_file_path: bool = False, opt_dtypes: bool = False, **kwargs
) -> pl.DataFrame:
    return _read_csv_file(
        path=path,
        self=self,
        include_file_path=include_file_path,
        opt_dtypes=opt_dtypes,
        **kwargs,
    )


def _read_csv(
    self,
    path: str | list[str],
    include_file_path: bool = False,
    use_threads: bool = True,
    concat: bool = True,
    verbose: bool = False,
    opt_dtypes: bool = False,
    **kwargs,
) -> pl.DataFrame | list[pl.DataFrame]:
    """
    Read a CSV file or a list of CSV files into a polars DataFrame.

    Args:
        path: (str | list[str]) Path to the CSV file(s).
        include_file_path: (bool, optional) If True, return a DataFrame with a 'file_path' column.
            Defaults to False.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        opt_dtypes: (bool, optional) If True, optimize DataFrame dtypes. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        (pl.DataFrame | list[pl.DataFrame]): Polars DataFrame or list of DataFrames.
    """
    if isinstance(path, str):
        path = path_to_glob(path, format="csv")
        path = self.glob(path)

    if isinstance(path, list):
        if use_threads:
            dfs = run_parallel(
                _read_csv_file,
                path,
                self=self,
                include_file_path=include_file_path,
                opt_dtypes=opt_dtypes,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        else:
            dfs = [
                _read_csv_file(
                    p,
                    self=self,
                    include_file_path=include_file_path,
                    opt_dtypes=opt_dtypes,
                    **kwargs,
                )
                for p in path
            ]
    else:
        dfs = _read_csv_file(
            path,
            self=self,
            include_file_path=include_file_path,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
    if concat:
        result = pl.concat(dfs, how="diagonal_relaxed")
        # if opt_dtypes:
        #    result = opt_dtype_pl(result, strict=False)
        return result
    return dfs


def _read_csv_batches(
    self: AbstractFileSystem,
    path: str | list[str],
    batch_size: int | None = None,
    include_file_path: bool = False,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    opt_dtypes: bool = False,
    **kwargs: Any,
) -> Generator[pl.DataFrame | list[pl.DataFrame], None, None]:
    """Process CSV files in batches with optional parallel reading.

    Internal generator function that handles batched reading of CSV files
    with support for parallel processing within each batch.

    Args:
        path: Path(s) to CSV file(s). Glob patterns supported.
        batch_size: Number of files to process in each batch
        include_file_path: Add source filepath as a column
        concat: Combine files within each batch
        use_threads: Enable parallel file reading within batches
        verbose: Print progress information
        opt_dtypes: Optimize DataFrame dtypes
        **kwargs: Additional arguments passed to pl.read_csv()

    Yields:
        Each batch of data in requested format:
        - pl.DataFrame: Single DataFrame if concat=True
        - list[pl.DataFrame]: List of DataFrames if concat=False

    Example:
        >>> fs = LocalFileSystem()
        >>> # Process large dataset in batches
        >>> for batch in fs._read_csv_batches(
        ...     "data/*.csv",
        ...     batch_size=100,
        ...     include_file_path=True,
        ...     verbose=True
        ... ):
        ...     print(f"Batch columns: {batch.columns}")
        >>>
        >>> # Parallel processing without concatenation
        >>> for batch in fs._read_csv_batches(
        ...     ["file1.csv", "file2.csv"],
        ...     batch_size=1,
        ...     concat=False,
        ...     use_threads=True
        ... ):
        ...     for df in batch:
        ...         print(f"DataFrame shape: {df.shape}")
    """
    # Handle path resolution
    if isinstance(path, str):
        path = path_to_glob(path, format="csv")
        path = self.glob(path)

    # Ensure path is a list
    if isinstance(path, str):
        path = [path]

    # Process files in batches
    for i in range(0, len(path), batch_size):
        batch_paths = path[i : i + batch_size]

        # Read batch with optional parallelization
        if use_threads and len(batch_paths) > 1:
            batch_dfs = run_parallel(
                _read_csv_file,
                batch_paths,
                self=self,
                include_file_path=include_file_path,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                opt_dtypes=opt_dtypes,
                **kwargs,
            )
        else:
            batch_dfs = [
                _read_csv_file(
                    p,
                    self=self,
                    include_file_path=include_file_path,
                    opt_dtypes=opt_dtypes,
                    **kwargs,
                )
                for p in batch_paths
            ]

        # if opt_dtypes:
        #    batch_dfs = [opt_dtype_pl(df, strict=False) for df in batch_dfs]

        if concat and len(batch_dfs) > 1:
            result = pl.concat(batch_dfs, how="diagonal_relaxed")
            # if opt_dtypes:
            #    result = opt_dtype_pl(result, strict=False)
            yield result
        else:
            yield batch_dfs


def read_csv(
    self: AbstractFileSystem,
    path: str | list[str],
    batch_size: int | None = None,
    include_file_path: bool = False,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    opt_dtypes: bool = False,
    **kwargs: Any,
) -> (
    pl.DataFrame
    | list[pl.DataFrame]
    | Generator[pl.DataFrame | list[pl.DataFrame], None, None]
):
    """Read CSV data from one or more files with powerful options.

    Provides a flexible interface for reading CSV files with support for:
    - Single file or multiple files
    - Batch processing for large datasets
    - Parallel processing
    - File path tracking
    - Polars DataFrame output

    Args:
        path: Path(s) to CSV file(s). Can be:
            - Single path string (globs supported)
            - List of path strings
        batch_size: If set, enables batch reading with this many files per batch
        include_file_path: Add source filepath as a column
        concat: Combine multiple files/batches into single DataFrame
        use_threads: Enable parallel file reading
        verbose: Print progress information
        **kwargs: Additional arguments passed to pl.read_csv()

    Returns:
        Various types depending on arguments:
        - pl.DataFrame: Single or concatenated DataFrame
        - list[pl.DataFrame]: List of DataFrames (if concat=False)
        - Generator: If batch_size set, yields batches of above types

    Example:
        >>> fs = LocalFileSystem()
        >>> # Read all CSVs in directory
        >>> df = fs.read_csv(
        ...     "data/*.csv",
        ...     include_file_path=True
        ... )
        >>> print(df.columns)
        ['file_path', 'col1', 'col2', ...]
        >>>
        >>> # Batch process large dataset
        >>> for batch_df in fs.read_csv(
        ...     "logs/*.csv",
        ...     batch_size=100,
        ...     use_threads=True,
        ...     verbose=True
        ... ):
        ...     print(f"Processing {len(batch_df)} rows")
        >>>
        >>> # Multiple files without concatenation
        >>> dfs = fs.read_csv(
        ...     ["file1.csv", "file2.csv"],
        ...     concat=False,
        ...     use_threads=True
        ... )
        >>> print(f"Read {len(dfs)} files")
    """
    if batch_size is not None:
        return _read_csv_batches(
            self=self,
            path=path,
            batch_size=batch_size,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
    return _read_csv(
        self=self,
        path=path,
        include_file_path=include_file_path,
        concat=concat,
        use_threads=use_threads,
        verbose=verbose,
        opt_dtypes=opt_dtypes,
        **kwargs,
    )


def _read_parquet_file(
    path: str,
    self: AbstractFileSystem,
    include_file_path: bool = False,
    opt_dtypes: bool = False,
    **kwargs: Any,
) -> pa.Table:
    """Read a single Parquet file from any filesystem.

    Internal function that handles reading individual Parquet files and
    optionally adds the source filepath as a column.

    Args:
        path: Path to Parquet file
        self: Filesystem instance to use for reading
        include_file_path: Add source filepath as a column
        opt_dtypes: Optimize DataFrame dtypes
        **kwargs: Additional arguments passed to pq.read_table()

    Returns:
        pa.Table: PyArrow Table containing Parquet data

    Example:
        >>> fs = LocalFileSystem()
        >>> table = _read_parquet_file(
        ...     "data.parquet",
        ...     fs,
        ...     include_file_path=True,
        ...     use_threads=True
        ... )
        >>> print("file_path" in table.column_names)
        True
    """
    if not path.endswith(".parquet"):
        raise ValueError(
            f"Path '{path}' does not point to a Parquet file. "
            "Ensure the path ends with '.parquet'."
        )
    table = pq.read_table(path, filesystem=self, **kwargs)
    if include_file_path:
        table = table.add_column(0, "file_path", pl.Series([path] * table.num_rows))
    if opt_dtypes:
        table = opt_dtype_pa(table, strict=False)
    return table


def read_parquet_file(
    self, path: str, include_file_path: bool = False, opt_dtypes: bool = False, **kwargs
) -> pa.Table:
    """Read a single Parquet file from any filesystem.

    Internal function that handles reading individual Parquet files and
    optionally adds the source filepath as a column.

    Args:
        path: Path to Parquet file
        include_file_path: Add source filepath as a column
        opt_dtypes: Optimize DataFrame dtypes
        **kwargs: Additional arguments passed to pq.read_table()

    Returns:
        pa.Table: PyArrow Table containing Parquet data

    Example:
        >>> fs = LocalFileSystem()
        >>> table = fs.read_parquet_file(
        ...     "data.parquet",
        ...     include_file_path=True,
        ...     use_threads=True
        ... )
        >>> print("file_path" in table.column_names)
        True
    """
    return _read_parquet_file(
        path=path,
        self=self,
        include_file_path=include_file_path,
        opt_dtypes=opt_dtypes,
        **kwargs,
    )


def _read_parquet(
    self,
    path: str | list[str],
    include_file_path: bool = False,
    use_threads: bool = True,
    concat: bool = True,
    verbose: bool = False,
    opt_dtypes: bool = False,
    **kwargs,
) -> pa.Table | list[pa.Table]:
    """
    Read a Parquet file or a list of Parquet files into a pyarrow Table.

    Args:
        path: (str | list[str]) Path to the Parquet file(s).
        include_file_path: (bool, optional) If True, return a Table with a 'file_path' column.
            Defaults to False.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        concat: (bool, optional) If True, concatenate the Tables. Defaults to True.
        **kwargs: Additional keyword arguments.

    Returns:
        (pa.Table | list[pa.Table]): Pyarrow Table or list of Pyarrow Tables.
    """
    # if not include_file_path and concat:
    #    if isinstance(path, str):
    #        path = path.replace("**", "").replace("*.parquet", "")
    #    table = _read_parquet_file(path, self=self, opt_dtypes=opt_dtypes, **kwargs)
    #    return table
    # else:
    if isinstance(path, str):
        path = path_to_glob(path, format="parquet")
        path = self.glob(path)

    if isinstance(path, list):
        if use_threads:
            tables = run_parallel(
                _read_parquet_file,
                path,
                self=self,
                include_file_path=include_file_path,
                opt_dtypes=opt_dtypes,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        else:
            tables = [
                _read_parquet_file(
                    p,
                    self=self,
                    include_file_path=include_file_path,
                    opt_dtypes=opt_dtypes,
                    **kwargs,
                )
                for p in path
            ]
    else:
        tables = _read_parquet_file(
            path=path,
            self=self,
            include_file_path=include_file_path,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
    if concat:
        # Unify schemas before concatenation if opt_dtypes or multiple tables
        if isinstance(tables, list):
            # if len(tables) > 1:
            #    schemas = [t.schema for t in tables]
            #    unified_schema = unify_schemas_pa(schemas)
            #    tables = [cast_schema(t, unified_schema) for t in tables]
            result = pa.concat_tables(
                [table for table in tables if table.num_rows > 0],
                promote_options="permissive",
            )
            # if opt_dtypes:
            #    result = opt_dtype_pa(result, strict=False)
            return result
        elif isinstance(tables, pa.Table):
            # if opt_dtypes:
            #    tables = opt_dtype_pa(tables, strict=False)
            return tables
        else:
            return pa.concat_tables(
                [table for table in tables if table.num_rows > 0],
                promote_options="permissive",
            )
    return tables


def _read_parquet_batches(
    self: AbstractFileSystem,
    path: str | list[str],
    batch_size: int | None = None,
    include_file_path: bool = False,
    use_threads: bool = True,
    concat: bool = True,
    verbose: bool = False,
    opt_dtypes: bool = False,
    **kwargs: Any,
) -> Generator[pa.Table | list[pa.Table], None, None]:
    """Process Parquet files in batches with performance optimizations.

    Internal generator function that handles batched reading of Parquet files
    with support for:
    - Parallel processing within batches
    - Metadata-based optimizations
    - Memory-efficient processing
    - Progress tracking

    Uses fast path for simple cases:
    - Single directory with _metadata
    - No need for filepath column
    - Concatenated output

    Args:
        path: Path(s) to Parquet file(s). Glob patterns supported.
        batch_size: Number of files to process in each batch
        include_file_path: Add source filepath as a column
        use_threads: Enable parallel file reading within batches
        concat: Combine files within each batch
        verbose: Print progress information
        **kwargs: Additional arguments passed to pq.read_table()

    Yields:
        Each batch of data in requested format:
        - pa.Table: Single Table if concat=True
        - list[pa.Table]: List of Tables if concat=False

    Example:
        >>> fs = LocalFileSystem()
        >>> # Fast path for simple case
        >>> next(_read_parquet_batches(
        ...     fs,
        ...     "data/",  # Contains _metadata
        ...     batch_size=1000
        ... ))
        >>>
        >>> # Parallel batch processing
        >>> for batch in fs._read_parquet_batches(
        ...     fs,
        ...     ["file1.parquet", "file2.parquet"],
        ...     batch_size=1,
        ...     include_file_path=True,
        ...     use_threads=True
        ... ):
        ...     print(f"Batch schema: {batch.schema}")
    """
    # Fast path for simple cases
    # if not include_file_path and concat and batch_size is None:
    #    if isinstance(path, str):
    #        path = path.replace("**", "").replace("*.parquet", "")
    #    table = _read_parquet_file(
    #        path=path, self=self, opt_dtypes=opt_dtypes, **kwargs
    #    )
    #    yield table
    #    return

    # Resolve path(s) to list
    if isinstance(path, str):
        path = path_to_glob(path, format="parquet")
        path = self.glob(path)

    if not isinstance(path, list):
        yield _read_parquet_file(
            path=path,
            self=self,
            include_file_path=include_file_path,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
        return

    # Process in batches
    for i in range(0, len(path), batch_size):
        batch_paths = path[i : i + batch_size]
        if use_threads and len(batch_paths) > 1:
            batch_tables = run_parallel(
                _read_parquet_file,
                batch_paths,
                self=self,
                include_file_path=include_file_path,
                opt_dtypes=opt_dtypes,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        else:
            batch_tables = [
                _read_parquet_file(
                    p,
                    self=self,
                    include_file_path=include_file_path,
                    opt_dtypes=opt_dtypes,
                    **kwargs,
                )
                for p in batch_paths
            ]

        if concat and batch_tables:
            # Unify schemas before concatenation
            if len(batch_tables) > 1:
                schemas = [t.schema for t in batch_tables]
                unified_schema = unify_schemas_pa(schemas)
                batch_tables = [cast_schema(t, unified_schema) for t in batch_tables]
            batch_table = pa.concat_tables(
                [table for table in batch_tables if table.num_rows > 0],
                promote_options="permissive",
            )
            # if opt_dtypes:
            #    result = opt_dtype_pa(result, strict=False)
            yield batch_table
        else:
            # if opt_dtypes and isinstance(batch_tables, list):
            #    batch_tables = [opt_dtype_pa(t, strict=False) for t in batch_tables]
            yield batch_tables


def read_parquet(
    self: AbstractFileSystem,
    path: str | list[str],
    batch_size: int | None = None,
    include_file_path: bool = False,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    opt_dtypes: bool = False,
    **kwargs: Any,
) -> pa.Table | list[pa.Table] | Generator[pa.Table | list[pa.Table], None, None]:
    """Read Parquet data with advanced features and optimizations.

    Provides a high-performance interface for reading Parquet files with support for:
    - Single file or multiple files
    - Batch processing for large datasets
    - Parallel processing
    - File path tracking
    - Automatic concatenation
    - PyArrow Table output

    The function automatically uses optimal reading strategies:
    - Direct dataset reading for simple cases
    - Parallel processing for multiple files
    - Batched reading for memory efficiency

    Args:
        path: Path(s) to Parquet file(s). Can be:
            - Single path string (globs supported)
            - List of path strings
            - Directory containing _metadata file
        batch_size: If set, enables batch reading with this many files per batch
        include_file_path: Add source filepath as a column
        concat: Combine multiple files/batches into single Table
        use_threads: Enable parallel file reading
        verbose: Print progress information
        opt_dtypes: Optimize Table dtypes for performance
        **kwargs: Additional arguments passed to pq.read_table()

    Returns:
        Various types depending on arguments:
        - pa.Table: Single or concatenated Table
        - list[pa.Table]: List of Tables (if concat=False)
        - Generator: If batch_size set, yields batches of above types

    Example:
        >>> fs = LocalFileSystem()
        >>> # Read all Parquet files in directory
        >>> table = fs.read_parquet(
        ...     "data/*.parquet",
        ...     include_file_path=True
        ... )
        >>> print(table.column_names)
        ['file_path', 'col1', 'col2', ...]
        >>>
        >>> # Batch process large dataset
        >>> for batch in fs.read_parquet(
        ...     "data/*.parquet",
        ...     batch_size=100,
        ...     use_threads=True
        ... ):
        ...     print(f"Processing {batch.num_rows} rows")
        >>>
        >>> # Read from directory with metadata
        >>> table = fs.read_parquet(
        ...     "data/",  # Contains _metadata
        ...     use_threads=True
        ... )
        >>> print(f"Total rows: {table.num_rows}")
    """
    if batch_size is not None:
        return _read_parquet_batches(
            self=self,
            path=path,
            batch_size=batch_size,
            include_file_path=include_file_path,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
    return _read_parquet(
        self=self,
        path=path,
        include_file_path=include_file_path,
        use_threads=use_threads,
        concat=concat,
        verbose=verbose,
        opt_dtypes=opt_dtypes,
        **kwargs,
    )


def read_files(
    self: AbstractFileSystem,
    path: str | list[str],
    format: str,
    batch_size: int | None = None,
    include_file_path: bool = False,
    concat: bool = True,
    jsonlines: bool = False,
    use_threads: bool = True,
    verbose: bool = False,
    opt_dtypes: bool = False,
    **kwargs: Any,
) -> (
    pl.DataFrame
    | pa.Table
    | list[pl.DataFrame]
    | list[pa.Table]
    | Generator[
        pl.DataFrame | pa.Table | list[pl.DataFrame] | list[pa.Table], None, None
    ]
):
    """Universal interface for reading data files of any supported format.

    A unified API that automatically delegates to the appropriate reading function
    based on file format, while preserving all advanced features like:
    - Batch processing
    - Parallel reading
    - File path tracking
    - Format-specific optimizations

    Args:
        path: Path(s) to data file(s). Can be:
            - Single path string (globs supported)
            - List of path strings
        format: File format to read. Supported values:
            - "json": Regular JSON or JSON Lines
            - "csv": CSV files
            - "parquet": Parquet files
        batch_size: If set, enables batch reading with this many files per batch
        include_file_path: Add source filepath as column/field
        concat: Combine multiple files/batches into single result
        jsonlines: For JSON format, whether to read as JSON Lines
        use_threads: Enable parallel file reading
        verbose: Print progress information
        opt_dtypes: Optimize DataFrame/Arrow Table dtypes for performance
        **kwargs: Additional format-specific arguments

    Returns:
        Various types depending on format and arguments:
        - pl.DataFrame: For CSV and optionally JSON
        - pa.Table: For Parquet
        - list[pl.DataFrame | pa.Table]: Without concatenation
        - Generator: If batch_size set, yields batches

    Example:
        >>> fs = LocalFileSystem()
        >>> # Read CSV files
        >>> df = fs.read_files(
        ...     "data/*.csv",
        ...     format="csv",
        ...     include_file_path=True
        ... )
        >>> print(type(df))
        <class 'polars.DataFrame'>
        >>>
        >>> # Batch process Parquet files
        >>> for batch in fs.read_files(
        ...     "data/*.parquet",
        ...     format="parquet",
        ...     batch_size=100,
        ...     use_threads=True
        ... ):
        ...     print(f"Batch type: {type(batch)}")
        >>>
        >>> # Read JSON Lines
        >>> df = fs.read_files(
        ...     "logs/*.jsonl",
        ...     format="json",
        ...     jsonlines=True,
        ...     concat=True
        ... )
        >>> print(df.columns)
    """
    if format == "json":
        if batch_size is not None:
            return read_json(
                self=self,
                path=path,
                batch_size=batch_size,
                include_file_path=include_file_path,
                jsonlines=jsonlines,
                concat=concat,
                use_threads=use_threads,
                verbose=verbose,
                opt_dtypes=opt_dtypes,
                **kwargs,
            )
        return read_json(
            self=self,
            path=path,
            include_file_path=include_file_path,
            jsonlines=jsonlines,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
    elif format == "csv":
        if batch_size is not None:
            return read_csv(
                self=self,
                path=path,
                batch_size=batch_size,
                include_file_path=include_file_path,
                concat=concat,
                use_threads=use_threads,
                verbose=verbose,
                opt_dtypes=opt_dtypes,
                **kwargs,
            )
        return read_csv(
            self=self,
            path=path,
            include_file_path=include_file_path,
            use_threads=use_threads,
            concat=concat,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )
    elif format == "parquet":
        if batch_size is not None:
            return read_parquet(
                self=self,
                path=path,
                batch_size=batch_size,
                include_file_path=include_file_path,
                concat=concat,
                use_threads=use_threads,
                verbose=verbose,
                opt_dtypes=opt_dtypes,
                **kwargs,
            )
        return read_parquet(
            self=self,
            path=path,
            include_file_path=include_file_path,
            use_threads=use_threads,
            concat=concat,
            verbose=verbose,
            opt_dtypes=opt_dtypes,
            **kwargs,
        )


def pyarrow_dataset(
    self: AbstractFileSystem,
    path: str,
    format: str = "parquet",
    schema: pa.Schema | None = None,
    partitioning: str | list[str] | pds.Partitioning = None,
    **kwargs: Any,
) -> pds.Dataset:
    """Create a PyArrow dataset from files in any supported format.

    Creates a dataset that provides optimized reading and querying capabilities
    including:
    - Schema inference and enforcement
    - Partition discovery and pruning
    - Predicate pushdown
    - Column projection

    Args:
        path: Base path to dataset files
        format: File format. Currently supports:
            - "parquet" (default)
            - "csv"
            - "json" (experimental)
        schema: Optional schema to enforce. If None, inferred from data.
        partitioning: How the dataset is partitioned. Can be:
            - str: Single partition field
            - list[str]: Multiple partition fields
            - pds.Partitioning: Custom partitioning scheme
        **kwargs: Additional arguments for dataset creation

    Returns:
        pds.Dataset: PyArrow dataset instance

    Example:
        >>> fs = LocalFileSystem()
        >>> # Simple Parquet dataset
        >>> ds = fs.pyarrow_dataset("data/")
        >>> print(ds.schema)
        >>>
        >>> # Partitioned dataset
        >>> ds = fs.pyarrow_dataset(
        ...     "events/",
        ...     partitioning=["year", "month"]
        ... )
        >>> # Query with partition pruning
        >>> table = ds.to_table(
        ...     filter=(ds.field("year") == 2024)
        ... )
        >>>
        >>> # CSV with schema
        >>> ds = fs.pyarrow_dataset(
        ...     "logs/",
        ...     format="csv",
        ...     schema=pa.schema([
        ...         ("timestamp", pa.timestamp("s")),
        ...         ("level", pa.string()),
        ...         ("message", pa.string())
        ...     ])
        ... )
    """
    return pds.dataset(
        path,
        filesystem=self,
        partitioning=partitioning,
        schema=schema,
        format=format,
        **kwargs,
    )


def pyarrow_parquet_dataset(
    self: AbstractFileSystem,
    path: str,
    schema: pa.Schema | None = None,
    partitioning: str | list[str] | pds.Partitioning = None,
    **kwargs: Any,
) -> pds.Dataset:
    """Create a PyArrow dataset optimized for Parquet files.

    Creates a dataset specifically for Parquet data, automatically handling
    _metadata files for optimized reading.

    This function is particularly useful for:
    - Datasets with existing _metadata files
    - Multi-file datasets that should be treated as one
    - Partitioned Parquet datasets

    Args:
        path: Path to dataset directory or _metadata file
        schema: Optional schema to enforce. If None, inferred from data.
        partitioning: How the dataset is partitioned. Can be:
            - str: Single partition field
            - list[str]: Multiple partition fields
            - pds.Partitioning: Custom partitioning scheme
        **kwargs: Additional dataset arguments

    Returns:
        pds.Dataset: PyArrow dataset instance

    Example:
        >>> fs = LocalFileSystem()
        >>> # Dataset with _metadata
        >>> ds = fs.pyarrow_parquet_dataset("data/_metadata")
        >>> print(ds.files)  # Shows all data files
        >>>
        >>> # Partitioned dataset directory
        >>> ds = fs.pyarrow_parquet_dataset(
        ...     "sales/",
        ...     partitioning=["year", "region"]
        ... )
        >>> # Query with partition pruning
        >>> table = ds.to_table(
        ...     filter=(
        ...         (ds.field("year") == 2024) &
        ...         (ds.field("region") == "EMEA")
        ...     )
        ... )
    """
    if not self.is_file(path):
        path = posixpath.join(path, "_metadata")
    return pds.dataset(
        path,
        filesystem=self,
        partitioning=partitioning,
        schema=schema,
        **kwargs,
    )


def pydala_dataset(
    self: AbstractFileSystem,
    path: str,
    partitioning: str | list[str] | pds.Partitioning = None,
    **kwargs: Any,
) -> ParquetDataset:  # type: ignore
    """Create a Pydala dataset for advanced Parquet operations.

    Creates a dataset with additional features beyond PyArrow including:
    - Delta table support
    - Schema evolution
    - Advanced partitioning
    - Metadata management
    - Sort key optimization

    Args:
        path: Path to dataset directory
        partitioning: How the dataset is partitioned. Can be:
            - str: Single partition field
            - list[str]: Multiple partition fields
            - pds.Partitioning: Custom partitioning scheme
        **kwargs: Additional dataset configuration

    Returns:
        ParquetDataset: Pydala dataset instance

    Example:
        >>> fs = LocalFileSystem()
        >>> # Create dataset
        >>> ds = fs.pydala_dataset(
        ...     "data/",
        ...     partitioning=["date"]
        ... )
        >>>
        >>> # Write with delta support
        >>> ds.write_to_dataset(
        ...     new_data,
        ...     mode="delta",
        ...     delta_subset=["id"]
        ... )
        >>>
        >>> # Read with metadata
        >>> df = ds.to_polars()
        >>> print(df.columns)
    """
    return ParquetDataset(
        path,
        filesystem=self,
        partitioning=partitioning,
        **kwargs,
    )


def write_parquet(
    self: AbstractFileSystem,
    data: pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict | list[dict],
    path: str,
    schema: pa.Schema | None = None,
    **kwargs: Any,
) -> pq.FileMetaData:
    """Write data to a Parquet file with automatic format conversion.

    Handles writing data from multiple input formats to Parquet with:
    - Automatic conversion to PyArrow
    - Schema validation/coercion
    - Metadata collection
    - Compression and encoding options

    Args:
        data: Input data in various formats:
            - Polars DataFrame/LazyFrame
            - PyArrow Table
            - Pandas DataFrame
            - Dict or list of dicts
        path: Output Parquet file path
        schema: Optional schema to enforce on write
        **kwargs: Additional arguments for pq.write_table()

    Returns:
        pq.FileMetaData: Metadata of written Parquet file

    Raises:
        SchemaError: If data doesn't match schema
        ValueError: If data cannot be converted

    Example:
        >>> fs = LocalFileSystem()
        >>> # Write Polars DataFrame
        >>> df = pl.DataFrame({
        ...     "id": range(1000),
        ...     "value": pl.Series(np.random.randn(1000))
        ... })
        >>> metadata = fs.write_parquet(
        ...     df,
        ...     "data.parquet",
        ...     compression="zstd",
        ...     compression_level=3
        ... )
        >>> print(f"Rows: {metadata.num_rows}")
        >>>
        >>> # Write with schema
        >>> schema = pa.schema([
        ...     ("id", pa.int64()),
        ...     ("value", pa.float64())
        ... ])
        >>> metadata = fs.write_parquet(
        ...     {"id": [1, 2], "value": [0.1, 0.2]},
        ...     "data.parquet",
        ...     schema=schema
        ... )
    """
    data = to_pyarrow_table(data, concat=False, unique=False)

    if schema is not None:
        data = cast_schema(data, schema)
    metadata = []
    pq.write_table(data, path, filesystem=self, metadata_collector=metadata, **kwargs)
    metadata = metadata[0]
    metadata.set_file_path(path)
    return metadata


def write_json(
    self: AbstractFileSystem,
    data: dict
    | pl.DataFrame
    | pl.LazyFrame
    | pa.Table
    | pd.DataFrame
    | dict
    | list[dict],
    path: str,
    append: bool = False,
) -> None:
    """Write data to a JSON file with flexible input support.

    Handles writing data in various formats to JSON or JSON Lines,
    with optional appending for streaming writes.

    Args:
        data: Input data in various formats:
            - Dict or list of dicts
            - Polars DataFrame/LazyFrame
            - PyArrow Table
            - Pandas DataFrame
        path: Output JSON file path
        append: Whether to append to existing file (JSON Lines mode)

    Example:
        >>> fs = LocalFileSystem()
        >>> # Write dictionary
        >>> data = {"name": "test", "values": [1, 2, 3]}
        >>> fs.write_json(data, "config.json")
        >>>
        >>> # Stream records
        >>> df1 = pl.DataFrame({"id": [1], "value": ["first"]})
        >>> df2 = pl.DataFrame({"id": [2], "value": ["second"]})
        >>> fs.write_json(df1, "stream.jsonl", append=False)
        >>> fs.write_json(df2, "stream.jsonl", append=True)
        >>>
        >>> # Convert PyArrow
        >>> table = pa.table({"a": [1, 2], "b": ["x", "y"]})
        >>> fs.write_json(table, "data.json")
    """
    if isinstance(data, pl.LazyFrame):
        data = data.collect()
    if isinstance(data, pl.DataFrame):
        data = data.to_arrow()
        data = cast_schema(
            data, convert_large_types_to_standard(data.schema)
        ).to_pydict()
    elif isinstance(data, pd.DataFrame):
        data = pa.Table.from_pandas(data, preserve_index=False).to_pydict()
    elif isinstance(data, pa.Table):
        data = data.to_pydict()
    if append:
        with self.open(path, "ab") as f:
            if isinstance(data, dict):
                f.write(orjson.dumps(data) + b"\n")
            else:
                for record in data:
                    f.write(orjson.dumps(record) + b"\n")
    else:
        with self.open(path, "wb") as f:
            f.write(orjson.dumps(data))


def write_csv(
    self: AbstractFileSystem,
    data: pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict | list[dict],
    path: str,
    append: bool = False,
    **kwargs: Any,
) -> None:
    """Write data to a CSV file with flexible input support.

    Handles writing data from multiple formats to CSV with options for:
    - Appending to existing files
    - Custom delimiters and formatting
    - Automatic type conversion
    - Header handling

    Args:
        data: Input data in various formats:
            - Polars DataFrame/LazyFrame
            - PyArrow Table
            - Pandas DataFrame
            - Dict or list of dicts
        path: Output CSV file path
        append: Whether to append to existing file
        **kwargs: Additional arguments for CSV writing:
            - delimiter: Field separator (default ",")
            - header: Whether to write header row
            - quote_char: Character for quoting fields
            - date_format: Format for date/time fields
            - float_precision: Decimal places for floats

    Example:
        >>> fs = LocalFileSystem()
        >>> # Write Polars DataFrame
        >>> df = pl.DataFrame({
        ...     "id": range(100),
        ...     "name": ["item_" + str(i) for i in range(100)]
        ... })
        >>> fs.write_csv(df, "items.csv")
        >>>
        >>> # Append records
        >>> new_items = pl.DataFrame({
        ...     "id": range(100, 200),
        ...     "name": ["item_" + str(i) for i in range(100, 200)]
        ... })
        >>> fs.write_csv(
        ...     new_items,
        ...     "items.csv",
        ...     append=True,
        ...     header=False
        ... )
        >>>
        >>> # Custom formatting
        >>> data = pa.table({
        ...     "date": [datetime.now()],
        ...     "value": [123.456]
        ... })
        >>> fs.write_csv(
        ...     data,
        ...     "formatted.csv",
        ...     date_format="%Y-%m-%d",
        ...     float_precision=2
        ... )
    """
    if isinstance(data, pl.LazyFrame):
        data = data.collect()
    if isinstance(data, pl.DataFrame):
        if append:
            with self.open(path, "ab") as f:
                data.write_csv(f, has_header=not append, **kwargs)
        else:
            with self.open(path, "wb") as f:
                data.write_csv(f, **kwargs)
    elif isinstance(data, (pa.Table, pd.DataFrame)):
        pl.from_arrow(pa.table(data)).write_csv(path, **kwargs)
    else:
        pl.DataFrame(data).write_csv(path, **kwargs)


def write_file(
    self,
    data: pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict,
    path: str,
    format: str,
    **kwargs,
) -> None:
    """
    Write a DataFrame to a file in the given format.

    Args:
        data: (pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame) Data to write.
        path (str): Path to write the data.
        format (str): Format of the file.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    if format == "json":
        write_json(self, data, path, **kwargs)
    elif format == "csv":
        write_csv(self, data, path, **kwargs)
    elif format == "parquet":
        write_parquet(self, data, path, **kwargs)


def write_files(
    self,
    data: (
        pl.DataFrame
        | pl.LazyFrame
        | pa.Table
        | pa.RecordBatch
        | pa.RecordBatchReader
        | pd.DataFrame
        | dict
        | list[
            pl.DataFrame
            | pl.LazyFrame
            | pa.Table
            | pa.RecordBatch
            | pa.RecordBatchReader
            | pd.DataFrame
            | dict
        ]
    ),
    path: str | list[str],
    basename: str = None,
    format: str = None,
    concat: bool = True,
    unique: bool | list[str] | str = False,
    mode: str = "append",  # append, overwrite, delete_matching, error_if_exists
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> None:
    """Write a DataFrame or a list of DataFrames to a file or a list of files.

    Args:
        data: (pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict | list[pl.DataFrame | pl.LazyFrame |
            pa.Table | pd.DataFrame | dict]) Data to write.
        path: (str | list[str]) Path to write the data.
        basename: (str, optional) Basename of the files. Defaults to None.
        format: (str, optional) Format of the data. Defaults to None.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        unique: (bool, optional) If True, remove duplicates. Defaults to False.
        mode: (str, optional) Write mode. Defaults to 'append'. Options: 'append', 'overwrite', 'delete_matching',
            'error_if_exists'.
        use_threads: (bool, optional) If True, use parallel processing. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        None

    Raises:
        FileExistsError: If file already exists and mode is 'error_if_exists'.
    """
    if not isinstance(data, list):
        data = [data]

    if concat:
        if isinstance(data[0], dict):
            data = _dict_to_dataframe(data)
        if isinstance(data[0], pl.LazyFrame):
            data = pl.concat([d.collect() for d in data], how="diagonal_relaxed")

        if isinstance(
            data[0], pa.Table | pa.RecordBatch | pa.RecordBatchReader | Generator
        ):
            data = pl.concat([pl.from_arrow(d) for d in data], how="diagonal_relaxed")
        elif isinstance(data[0], pd.DataFrame):
            data = pl.concat([pl.from_pandas(d) for d in data], how="diagonal_relaxed")

        if unique:
            data = data.unique(
                subset=None if not isinstance(unique, str | list) else unique,
                maintain_order=True,
            )

        data = [data]

    if format is None:
        format = (
            path[0].split(".")[-1]
            if isinstance(path, list) and "." in path[0]
            else path.split(".")[-1]
            if "." in path
            else "parquet"
        )

    def _write(d, p, basename, i):
        if f".{format}" not in p:
            if not basename:
                basename = f"data-{dt.datetime.now().strftime('%Y%m%d_%H%M%S%f')[:-3]}-{uuid.uuid4().hex[:16]}"
            p = f"{p}/{basename}-{i}.{format}"

        if mode == "delete_matching":
            write_file(self, d, p, format, **kwargs)
        elif mode == "overwrite":
            if self.exists(p):
                self.fs.rm(p, recursive=True)
            write_file(self, d, p, format, **kwargs)
        elif mode == "append":
            if not self.exists(p):
                write_file(self, d, p, format, **kwargs)
            else:
                p = p.replace(f".{format}", f"-{i}.{format}")
                write_file(self, d, p, format, **kwargs)
        elif mode == "error_if_exists":
            if self.exists(p):
                raise FileExistsError(f"File already exists: {p}")
            else:
                write_file(self, d, p, format, **kwargs)

    if mode == "overwrite":
        if isinstance(path, list):
            for p in path:
                # Remove existing files
                if self.exists(p):
                    self.rm(p, recursive=True)
        else:
            # Remove existing files
            if self.exists(path):
                self.rm(path, recursive=True)

    if use_threads:
        run_parallel(
            _write,
            d=data,
            p=path,
            basename=basename,
            i=list(range(len(data))),
            verbose=verbose,
        )
    else:
        for i, p in enumerate(path):
            _write(i, data, p, basename)


def write_pyarrow_dataset(
    self,
    data: (
        pl.DataFrame
        | pl.LazyFrame
        | pa.Table
        | pa.RecordBatch
        | pa.RecordBatchReader
        | pd.DataFrame
        | dict
        | list[
            pl.DataFrame
            | pl.LazyFrame
            | pa.Table
            | pa.RecordBatch
            | pa.RecordBatchReader
            | pd.DataFrame
            | dict
        ]
    ),
    path: str,
    basename: str | None = None,
    schema: pa.Schema | None = None,
    partition_by: str | list[str] | pds.Partitioning | None = None,
    partitioning_flavor: str = "hive",
    mode: str = "append",
    format: str | None = "parquet",
    compression: str = "zstd",
    max_rows_per_file: int | None = 2_500_000,
    row_group_size: int | None = 250_000,
    concat: bool = True,
    unique: bool | list[str] | str = False,
    **kwargs,
) -> list[pq.FileMetaData] | None:
    """
    Write a tabluar data to a PyArrow dataset.

    Args:
        data: (pl.DataFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader |
            pd.DataFrame | list[pl.DataFrame] | list[pa.Table] | list[pa.RecordBatch] |
            list[pa.RecordBatchReader] | list[pd.DataFrame]) Data to write.
        path: (str) Path to write the data.
        basename: (str, optional) Basename of the files. Defaults to None.
        schema: (pa.Schema, optional) Schema of the data. Defaults to None.
        partition_by: (str | list[str] | pds.Partitioning, optional) Partitioning of the data.
            Defaults to None.
        partitioning_flavor: (str, optional) Partitioning flavor. Defaults to 'hive'.
        mode: (str, optional) Write mode. Defaults to 'append'.
        format: (str, optional) Format of the data. Defaults to 'parquet'.
        compression: (str, optional) Compression algorithm. Defaults to 'zstd'.
        max_rows_per_file: (int, optional) Maximum number of rows per file. Defaults to 2_500_000.
        row_group_size: (int, optional) Row group size. Defaults to 250_000.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        unique: (bool | str | list[str], optional) If True, remove duplicates. Defaults to False.
        **kwargs: Additional keyword arguments for `pds.write_dataset`.

    Returns:
        (list[pq.FileMetaData] | None): List of Parquet file metadata or None.
    """
    data = to_pyarrow_table(data, concat=concat, unique=unique)

    if mode == "delete_matching":
        existing_data_behavior = "delete_matching"
    elif mode == "append":
        existing_data_behavior = "overwrite_or_ignore"
    elif mode == "overwrite":
        self.rm(path, recursive=True)
        existing_data_behavior = "overwrite_or_ignore"
    else:
        existing_data_behavior = mode

    if basename is None:
        basename_template = (
            "data-"
            f"{dt.datetime.now().strftime('%Y%m%d_%H%M%S%f')[:-3]}-{uuid.uuid4().hex[:16]}-{{i}}.parquet"
        )
    else:
        basename_template = f"{basename}-{{i}}.parquet"

    file_options = pds.ParquetFileFormat().make_write_options(compression=compression)

    create_dir: bool = (False,)

    if hasattr(self, "fs"):
        if "local" in self.fs.protocol:
            create_dir = True
    else:
        if "local" in self.protocol:
            create_dir = True

    if format == "parquet":
        metadata = []

        def file_visitor(written_file):
            file_metadata = written_file.metadata
            file_metadata.set_file_path(written_file.path)
            metadata.append(file_metadata)

    pds.write_dataset(
        data=data,
        base_dir=path,
        basename_template=basename_template,
        partitioning=partition_by,
        partitioning_flavor=partitioning_flavor,
        filesystem=self,
        existing_data_behavior=existing_data_behavior,
        min_rows_per_group=row_group_size,
        max_rows_per_group=row_group_size,
        max_rows_per_file=max_rows_per_file,
        schema=schema,
        format=format,
        create_dir=create_dir,
        file_options=file_options,
        file_visitor=file_visitor if format == "parquet" else None,
        **kwargs,
    )
    if format == "parquet":
        return metadata


def write_pydala_dataset(
    self,
    data: (
        pl.DataFrame
        | pl.LazyFrame
        | pa.Table
        | pa.RecordBatch
        | pa.RecordBatchReader
        | pd.DataFrame
        | dict
        | list[
            pl.DataFrame
            | pl.LazyFrame
            | pa.Table
            | pa.RecordBatch
            | pa.RecordBatchReader
            | pd.DataFrame
            | dict
        ]
    ),
    path: str,
    mode: str = "append",  # "delta", "overwrite"
    basename: str | None = None,
    partition_by: str | list[str] | None = None,
    partitioning_flavor: str = "hive",
    max_rows_per_file: int | None = 2_500_000,
    row_group_size: int | None = 250_000,
    compression: str = "zstd",
    concat: bool = True,
    sort_by: str | list[str] | list[tuple[str, str]] | None = None,
    unique: bool | str | list[str] = False,
    delta_subset: str | list[str] | None = None,
    update_metadata: bool = True,
    alter_schema: bool = False,
    timestamp_column: str | None = None,
    verbose: bool = False,
    **kwargs,
) -> None:
    """Write a tabular data to a Pydala dataset.

    Args:
        data: (pl.DataFrame | pa.Table | pa.RecordBatch | pa.RecordBatchReader |
            pd.DataFrame | list[pl.DataFrame] | list[pa.Table] | list[pa.RecordBatch] |
            list[pa.RecordBatchReader] | list[pd.DataFrame]) Data to write.
        path: (str) Path to write the data.
        mode: (str, optional) Write mode. Defaults to 'append'. Options: 'delta', 'overwrite'.
        basename: (str, optional) Basename of the files. Defaults to None.
        partition_by: (str | list[str], optional) Partitioning of the data. Defaults to None.
        partitioning_flavor: (str, optional) Partitioning flavor. Defaults to 'hive'.
        max_rows_per_file: (int, optional) Maximum number of rows per file. Defaults to 2_500_000.
        row_group_size: (int, optional) Row group size. Defaults to 250_000.
        compression: (str, optional) Compression algorithm. Defaults to 'zstd'.
        sort_by: (str | list[str] | list[tuple[str, str]], optional) Columns to sort by. Defaults to None.
        unique: (bool | str | list[str], optional) If True, ensure unique values. Defaults to False.
        delta_subset: (str | list[str], optional) Subset of columns to include in delta table. Defaults to None.
        update_metadata: (bool, optional) If True, update metadata. Defaults to True.
        alter_schema: (bool, optional) If True, alter schema. Defaults to False.
        timestamp_column: (str, optional) Timestamp column. Defaults to None.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments for `ParquetDataset.write_to_dataset`.

    Returns:
        None
    """
    data = to_pyarrow_table(data, concat=concat, unique=unique)

    ds = pydala_dataset(self=self, path=path, partitioning=partitioning_flavor)
    ds.write_to_dataset(
        data=data,
        mode=mode,
        basename=basename,
        partition_by=partition_by,
        max_rows_per_file=max_rows_per_file,
        row_group_size=row_group_size,
        compression=compression,
        sort_by=sort_by,
        unique=unique,
        delta_subset=delta_subset,
        update_metadata=update_metadata,
        alter_schema=alter_schema,
        timestamp_column=timestamp_column,
        verbose=verbose,
        **kwargs,
    )


AbstractFileSystem.read_json_file = read_json_file
AbstractFileSystem.read_json = read_json
AbstractFileSystem.read_csv_file = read_csv_file
AbstractFileSystem.read_csv = read_csv
AbstractFileSystem.read_parquet_file = read_parquet_file
AbstractFileSystem.read_parquet = read_parquet
AbstractFileSystem.read_files = read_files
AbstractFileSystem.pyarrow_dataset = pyarrow_dataset
AbstractFileSystem.pydala_dataset = pydala_dataset
AbstractFileSystem.pyarrow_parquet_dataset = pyarrow_parquet_dataset
AbstractFileSystem.write_parquet = write_parquet
AbstractFileSystem.write_json = write_json
AbstractFileSystem.write_csv = write_csv
AbstractFileSystem.write_file = write_file
AbstractFileSystem.write_files = write_files
AbstractFileSystem.write_pyarrow_dataset = write_pyarrow_dataset
AbstractFileSystem.write_pydala_dataset = write_pydala_dataset
