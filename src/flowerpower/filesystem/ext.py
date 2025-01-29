import datetime as dt
import posixpath
import uuid
from typing import Generator

import orjson
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pds
import pyarrow.parquet as pq
from fsspec import AbstractFileSystem

from ..utils.misc import (
    convert_large_types_to_standard,
    run_parallel,
    _dict_to_dataframe,
)
from ..utils.polars import pl

import importlib

if importlib.util.find_spec("duckdb") is not None:
    import duckdb
else:
    duckdb = None

if importlib.util.find_spec("pydala") is not None:
    from pydala.dataset import ParquetDataset
else:
    ParquetDataset = None


def read_json_file(
    path, self, include_file_path: bool = False, jsonlines: bool = False
) -> dict | list[dict]:
    with self.open(path) as f:
        if jsonlines:
            data = [orjson.loads(line) for line in f.readlines()]
        else:
            data = orjson.loads(f.read())
    if include_file_path:
        return {path: data}
    return data


def _read_json(
    self,
    path: str | list[str],
    include_file_path: bool = False,
    use_threads: bool = True,
    jsonlines: bool = False,
    as_dataframe: bool = True,
    concat: bool = True,
    verbose: bool = False,
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
        **kwargs: Additional keyword arguments.

    Returns:
        (dict | list[dict] | pl.DataFrame | list[pl.DataFrame]):
            Dictionary, list of dictionaries, DataFrame or list of DataFrames.
    """
    if isinstance(path, str):
        if "**" in path:
            path = self.glob(path)
        else:
            if ".json" not in posixpath.basename(path):
                path = posixpath.join(path, "**/*.jsonl" if jsonlines else "**/*.json")
                path = self.glob(path)

    if isinstance(path, list):
        if use_threads:
            data = run_parallel(
                read_json_file,
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
            read_json_file(
                path=p,
                self=self,
                include_file_path=include_file_path,
                jsonlines=jsonlines,
            )
            for p in path
        ]
    data = read_json_file(
        path=path, self=self, include_file_path=include_file_path, jsonlines=jsonlines
    )
    if as_dataframe:
        if not include_file_path:
            data = pl.DataFrame(data)
        else:
            data = pl.DataFrame(list(data.values())[0]).with_columns(
                pl.lit(list(data.keys())[0]).alias("file_path")
            )
        if concat:
            return pl.concat(data, how="diagonal_relaxed")
    return data


def _read_json_batches(
    self,
    path: str | list[str],
    batch_size: int | None = None,
    include_file_path: bool = False,
    jsonlines: bool = False,
    as_dataframe: bool = True,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> Generator[dict | list[dict] | pl.DataFrame | list[pl.DataFrame], None, None]:
    """
    Read JSON files in batches with optional parallel processing within batches.

    Args:
        path: (str | list[str]) Path to the JSON file(s).
        batch_size: (int | None) Number of files to process in each batch. Defaults to None.
        include_file_path: (bool) If True, return with file path as key.
        jsonlines: (bool) If True, read JSON lines. Defaults to False.
        as_dataframe: (bool) If True, return DataFrame. Defaults to True.
        concat: (bool) If True, concatenate batch DataFrames. Defaults to True.
        use_threads: (bool) If True, use parallel processing within batches.
        verbose: (bool) If True, print verbose output.
        **kwargs: Additional keyword arguments.

    Yields:
        Data from num_batches files as dict/DataFrame based on parameters.
    """
    # Handle path resolution
    if isinstance(path, str):
        if "**" in path:
            path = self.glob(path)
        else:
            if ".json" not in posixpath.basename(path):
                path = posixpath.join(path, "**/*.jsonl" if jsonlines else "**/*.json")
                path = self.glob(path)

    if isinstance(path, str):
        path = [path]

    # Process files in batches
    for i in range(0, len(path), batch_size):
        batch_paths = path[i : i + batch_size]

        # Read batch with optional parallelization
        if use_threads and len(batch_paths) > 1:
            batch_data = run_parallel(
                read_json_file,
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
                read_json_file(
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
                    pl.DataFrame(list(d.values())[0]).with_columns(
                        pl.lit(list(d.keys())[0]).alias("file_path")
                    )
                    for d in batch_data
                ]

            if concat and len(batch_dfs) > 1:
                yield pl.concat(batch_dfs, how="diagonal_relaxed")
            else:
                yield batch_dfs
        else:
            yield batch_data


def read_json(
    self,
    path: str | list[str],
    batch_size: int | None = None,
    include_file_path: bool = False,
    jsonlines: bool = False,
    as_dataframe: bool = True,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> (
    dict
    | list[dict]
    | pl.DataFrame
    | list[pl.DataFrame]
    | Generator[dict | list[dict] | pl.DataFrame | list[pl.DataFrame], None, None]
):
    """
    Read a JSON file or a list of JSON files. Optionally read in batches,
    returning a generator that sequentially yields data for specified number of files.

    Args:
        path: (str | list[str]) Path to the JSON file(s).
        batch_size: (int | None) Number of files to process in each batch. Defaults to None.
        include_file_path: (bool) If True, return with file path as key.
        jsonlines: (bool) If True, read JSON lines. Defaults to False.
        as_dataframe: (bool) If True, return DataFrame. Defaults to True.
        concat: (bool) If True, concatenate the DataFrames. Defaults to True.
        use_threads: (bool) If True, use parallel processing within batches. Defaults to True.
        verbose: (bool) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        (dict | list[dict] | pl.DataFrame | list[pl.DataFrame]:
            Dictionary, list of dictionaries, DataFrame, list of DataFrames
    Yields:
        (dict | list[dict] | pl.DataFrame | list[pl.DataFrame]:
            Dictionary, list of dictionaries, DataFrame, list of DataFrames
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
        **kwargs,
    )


def read_csv_file(
    path, self, include_file_path: bool = False, **kwargs
) -> pl.DataFrame:
    with self.open(path) as f:
        df = pl.read_csv(f, **kwargs)
    if include_file_path:
        return df.with_columns(pl.lit(path).alias("file_path"))
    return df


def _read_csv(
    self,
    path: str | list[str],
    include_file_path: bool = False,
    use_threads: bool = True,
    concat: bool = True,
    verbose: bool = False,
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
        **kwargs: Additional keyword arguments.

    Returns:
        (pl.DataFrame | list[pl.DataFrame]): Polars DataFrame or list of DataFrames.
    """
    if isinstance(path, str):
        if "**" in path:
            path = self.glob(path)
        else:
            if ".csv" not in posixpath.basename(path):
                path = posixpath.join(path, "**/*.csv")
                path = self.glob(path)

    if isinstance(path, list):
        if use_threads:
            dfs = run_parallel(
                read_csv_file,
                path,
                self=self,
                include_file_path=include_file_path,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        dfs = [
            read_csv_file(p, self=self, include_file_path=include_file_path, **kwargs)
            for p in path
        ]
    dfs = read_csv_file(
        path=path, self=self, include_file_path=include_file_path, **kwargs
    )
    if concat:
        return pl.concat(dfs, how="diagonal_relaxed")
    return dfs


def _read_csv_batches(
    self,
    path: str | list[str],
    batch_size: int | None = None,
    include_file_path: bool = False,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> Generator[pl.DataFrame, None, None]:
    """
    Read CSV files in batches with optional parallel processing within batches.

    Args:
        path: (str | list[str]) Path to the CSV file(s).
        batch_size: (int | None) Number of files to process in each batch. Defaults to None.
        include_file_path: (bool) If True, include file_path column.
        concat: (bool) If True, concatenate batch DataFrames.
        use_threads: (bool) If True, use parallel processing within batches.
        verbose: (bool) If True, print verbose output.
        **kwargs: Additional keyword arguments.

    Yields:
        pl.DataFrame: DataFrame containing data from num_batches files.
    """
    # Handle path resolution
    if isinstance(path, str):
        if "**" in path:
            path = self.glob(path)
        else:
            if ".csv" not in posixpath.basename(path):
                path = posixpath.join(path, "**/*.csv")
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
                read_csv_file,
                batch_paths,
                self=self,
                include_file_path=include_file_path,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        else:
            batch_dfs = [
                read_csv_file(
                    p, self=self, include_file_path=include_file_path, **kwargs
                )
                for p in batch_paths
            ]

        if concat and len(batch_dfs) > 1:
            yield pl.concat(batch_dfs, how="diagonal_relaxed")
        else:
            yield batch_dfs


def read_csv(
    self,
    path: str | list[str],
    batch_size: int | None = None,
    include_file_path: bool = False,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> (
    pl.DataFrame
    | list[pl.DataFrame]
    | Generator[pl.DataFrame | list[pl.DataFrame], None, None]
):
    """
    Read a CSV file or a list of CSV files. Optionally read in batches,
    returning a generator that sequentially yields data for specified number of files.

    Args:
        path: (str | list[str]) Path to the CSV file(s).
        batch_size: (int | None) Number of files to process in each batch. Defaults to None.
        include_file_path: (bool, optional) If True, include 'file_path' column.
        concat: (bool, optional) If True, concatenate the batch DataFrames. Defaults to True.
        use_threads: (bool, optional) If True, use parallel processing within batches. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        pl.DataFrame | list[pl.DataFrame]:
            DataFrame or list or DataFrames containing data from num_batches files.

    Yields:
        pl.DataFrame | list[pl.DataFrame]:
            DataFrame or list of DataFrames containing data from num_batches files.
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
            **kwargs,
        )
    return _read_csv(
        self=self,
        path=path,
        include_file_path=include_file_path,
        concat=concat,
        use_threads=use_threads,
        verbose=verbose,
        **kwargs,
    )


def read_parquet_file(
    path, self, include_file_path: bool = False, **kwargs
) -> pa.Table:
    table = pq.read_table(path, filesystem=self, **kwargs)
    if include_file_path:
        return table.add_column(0, "file_path", pl.Series([path] * table.num_rows))
    return table


def _read_parquet(
    self,
    path,
    include_file_path: bool = False,
    use_threads: bool = True,
    concat: bool = True,
    verbose: bool = False,
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
    if not include_file_path and concat:
        path = path.replace("**", "").replace("*.parquet", "")
        return pq.read_table(path, filesystem=self, **kwargs)
    else:
        if isinstance(path, str):
            if "**" in path:
                if "*.parquet" in path:
                    path = posixpath.join(path, "*.parquet")

                path = self.glob(path)
            else:
                if ".parquet" in path:
                    path = posixpath.join(path, "**/*.parquet")
                path = self.glob(path)

        if isinstance(path, list):
            if use_threads:
                table = run_parallel(
                    read_parquet_file,
                    path,
                    self=self,
                    include_file_path=include_file_path,
                    n_jobs=-1,
                    backend="threading",
                    verbose=verbose,
                    **kwargs,
                )
            else:
                table = [
                    read_parquet_file(
                        p, self=self, include_file_path=include_file_path, **kwargs
                    )
                    for p in path
                ]
        else:
            table = read_parquet_file(
                path=path, self=self, include_file_path=include_file_path, **kwargs
            )
    if concat:
        return pa.concat_tables(table, promote_options="permissive")
    return table


def _read_parquet_batches(
    self,
    path: str | list[str],
    batch_size: int | None = None,
    include_file_path: bool = False,
    use_threads: bool = True,
    concat: bool = True,
    verbose: bool = False,
    **kwargs,
) -> Generator[pa.Table | list[pa.Table], None, None]:
    """
    Read Parquet files in batches, yielding PyArrow Tables.

    Args:
        path: (str | list[str]) Path to the Parquet file(s).
        batch_size: (int | None) Number of files to process in each batch. Defaults to None.
        include_file_path: (bool) If True, return Tables with 'file_path' column. Defaults to False.
        use_threads: (bool) If True, read files in parallel within batches. Defaults to True.
        concat: (bool) If True, concatenate Tables within each batch. Defaults to True.
        verbose: (bool) If True, print progress information. Defaults to False.
        **kwargs: Additional keyword arguments.

    Yields:
        pa.Table | list[pa.Table]: Table or list of Tables per batch.
    """
    # Fast path for simple cases
    if not include_file_path and concat and batch_size is None:
        path = path.replace("**", "").replace("*.parquet", "")
        yield pq.read_table(path, filesystem=self, **kwargs)
        return

    # Resolve path(s) to list
    if isinstance(path, str):
        if "**" in path:
            if "*.parquet" not in path:
                path = posixpath.join(path, "**/*.parquet")
            path = self.glob(path)
        else:
            if ".parquet" not in path:
                path = posixpath.join(path, "**/*.parquet")
            path = self.glob(path)

    if not isinstance(path, list):
        yield read_parquet_file(
            path=path, self=self, include_file_path=include_file_path, **kwargs
        )
        return

    # Process in batches

    for i in range(0, len(path), batch_size):
        batch_paths = path[i : i + batch_size]
        if use_threads and len(batch_paths) > 1:
            batch_tables = run_parallel(
                read_parquet_file,
                batch_paths,
                self=self,
                include_file_path=include_file_path,
                n_jobs=-1,
                backend="threading",
                verbose=verbose,
                **kwargs,
            )
        else:
            batch_tables = [
                read_parquet_file(
                    p, self=self, include_file_path=include_file_path, **kwargs
                )
                for p in batch_paths
            ]

        if concat and batch_tables:
            yield pa.concat_tables(batch_tables, promote_options="permissive")
        else:
            yield batch_tables


def read_parquet(
    self,
    path: str | list[str],
    batch_size: int | None = None,
    include_file_path: bool = False,
    concat: bool = True,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> pa.Table | list[pa.Table] | Generator[pa.Table | list[pa.Table], None, None]:
    """
    Read a Parquet file or a list of Parquet files. Optionally read in batches,
    returning a generator that sequentially yields data for specified number of files.

    Args:
        path: (str | list[str]) Path to the Parquet file(s).
        batch_size: (int | None) Number of files to process in each batch. Defaults to None.
        include_file_path: (bool, optional) If True, include 'file_path' column.
        concat: (bool, optional) If True, concatenate the batch Tables. Defaults to True.
        use_threads: (bool, optional) If True, use parallel processing within batches. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        pa.Table | list[pa.Table]:
            PyArrow Table or list of PyArrow Tables containing data from num_batches files.

    Yields:
        pa.Table | list[pa.Table]: PyArrow Table or list of PyArrow Tables containing data from num_batches files.
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
            **kwargs,
        )
    return _read_parquet(
        self=self,
        path=path,
        include_file_path=include_file_path,
        use_threads=use_threads,
        concat=concat,
        verbose=verbose,
        **kwargs,
    )


def read_files(
    self,
    path: str | list[str],
    format: str,
    batch_size: int | None = None,
    include_file_path: bool = False,
    concat: bool = True,
    jsonlines: bool = False,
    use_threads: bool = True,
    verbose: bool = False,
    **kwargs,
) -> (
    pl.DataFrame
    | pa.Table
    | list[pl.DataFrame]
    | list[pa.Table]
    | Generator[
        pl.DataFrame | pa.Table | list[pa.Table] | list[pl.DataFrame], None, None
    ]
):
    """
    Read a file or a list of files of the given format.

    Args:
        path: (str | list[str]) Path to the file(s).
        format: (str) Format of the file.
        batch_size: (int | None) Number of files to process in each batch. Defaults to None.
        include_file_path: (bool, optional) If True, return a DataFrame with a 'file_path' column.
            Defaults to False.
        concat: (bool, optional) If True, concatenate the DataFrames. Defaults to True.
        jsonlines: (bool, optional) If True, read JSON lines. Defaults to False.
        use_threads: (bool, optional) If True, read files in parallel. Defaults to True.
        verbose: (bool, optional) If True, print verbose output. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        (pl.DataFrame | pa.Table | list[pl.DataFrame] | list[pa.Table]):
            Polars DataFrame, Pyarrow Table or list of DataFrames, LazyFrames or Tables.

    Yields:
        (pl.DataFrame | pa.Table):
            Polars DataFrame, Pyarrow Table or list of DataFrames, LazyFrames or Tables.
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
                **kwargs,
            )
        return read_json(
            self,
            path,
            include_file_path=include_file_path,
            jsonlines=jsonlines,
            concat=concat,
            use_threads=use_threads,
            verbose=verbose,
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
                **kwargs,
            )
        return read_csv(
            self,
            path,
            include_file_path=include_file_path,
            use_threads=use_threads,
            concat=concat,
            verbose=verbose,
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
                **kwargs,
            )
        return read_parquet(
            self,
            path,
            include_file_path=include_file_path,
            use_threads=use_threads,
            concat=concat,
            verbose=verbose,
            **kwargs,
        )


def pyarrow_dataset(
    self,
    path: str,
    format="parquet",
    schema: pa.Schema | None = None,
    partitioning: str | list[str] | pds.Partitioning = None,
    **kwargs,
) -> pds.Dataset:
    """
    Create a pyarrow dataset.

    Args:
        path: (str) Path to the dataset.
        format: (str, optional) Format of the dataset. Defaults to 'parquet'.
        schema: (pa.Schema, optional) Schema of the dataset. Defaults to None.
        partitioning: (str | list[str] | pds.Partitioning, optional) Partitioning of the dataset.
            Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        (pds.Dataset): Pyarrow dataset.
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
    self,
    path: str,
    schema: pa.Schema | None = None,
    partitioning: str | list[str] | pds.Partitioning = None,
    **kwargs,
) -> pds.Dataset:
    """
    Create a pyarrow dataset from a parquet_metadata file.

    Args:
        path: (str) Path to the dataset.
        schema: (pa.Schema, optional) Schema of the dataset. Defaults to None.
        partitioning: (str | list[str] | pds.Partitioning, optional) Partitioning of the dataset.
            Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        (pds.Dataset): Pyarrow dataset.
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
    self,
    path: str,
    partitioning: str | list[str] | pds.Partitioning = None,
    **kwargs,
) -> ParquetDataset:
    """
    Create a pydala dataset.

    Args:
        path: (str) Path to the dataset.
        partitioning: (str | list[str] | pds.Partitioning, optional) Partitioning of the dataset.
            Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        (ParquetDataset): Pydala dataset.
    """
    return ParquetDataset(
        path,
        filesystem=self,
        partitioning=partitioning,
        **kwargs,
    )


def write_parquet(
    self,
    data: pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict | list[dict],
    path: str,
    schema: pa.Schema | None = None,
    **kwargs,
) -> pq.FileMetaData:
    """
    Write a DataFrame to a Parquet file.

    Args:
        data: (pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame) Data to write.
        path: (str) Path to write the data.
        schema: (pa.Schema, optional) Schema of the data. Defaults to None.
        **kwargs: Additional keyword arguments for `pq.write_table`.

    Returns:
        (pq.FileMetaData): Parquet file metadata.
    """
    if isinstance(data, (dict | list)):
        data = _dict_to_dataframe(data)

    if isinstance(data, pl.LazyFrame):
        data = data.collect()
    elif isinstance(data, pl.DataFrame):
        data = data.to_arrow()
        data = data.cast(convert_large_types_to_standard(data.schema))
    elif isinstance(data, pd.DataFrame):
        data = pa.Table.from_pandas(data, preserve_index=False)

    if schema is not None:
        data = data.cast(schema)
    metadata = []
    pq.write_table(data, path, filesystem=self, metadata_collector=metadata, **kwargs)
    metadata = metadata[0]
    metadata.set_file_path(path)
    return metadata


def write_json(
    self,
    data: (
        dict | pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict | list[dict]
    ),
    path: str,
    append: bool = False,
) -> None:
    """
    Write a dictionary, DataFrame or Table to a JSON file.

    Args:
        data: (dict | pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame) Data to write.
        path: (str) Path to write the data.
        append: (bool, optional) If True, append to the file. Defaults to False.

    Returns:
        None
    """
    if isinstance(data, pl.LazyFrame):
        data = data.collect()
    if isinstance(data, pl.DataFrame):
        data = data.to_arrow()
        data = data.cast(convert_large_types_to_standard(data.schema)).to_pydict()
    elif isinstance(data, pd.DataFrame):
        data = pa.Table.from_pandas(data, preserve_index=False).to_pydict()
    elif isinstance(data, pa.Table):
        data = data.to_pydict()
    if append:
        with self.open(path, "ab") as f:
            f.write(orjson.dumps(data))
            f.write(b"\n")
    else:
        with self.open(path, "wb") as f:
            f.write(orjson.dumps(data))


def write_csv(
    self,
    data: pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict,
    path: str,
    **kwargs,
) -> None:
    """
    Write a DataFrame to a CSV file.

    Args:
        data: (pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame) Data to write.
        path: (str) Path to write the data.
        **kwargs: Additional keyword arguments for `pl.DataFrame.write_csv`.

    Returns:
        None
    """
    if isinstance(data, dict | list[dict]):
        data = _dict_to_dataframe(data)
    elif isinstance(data, pl.LazyFrame):
        data = data.collect()
    elif isinstance(data, pa.Table):
        data = pl.from_arrow(data)
    elif isinstance(data, pd.DataFrame):
        data = pl.from_pandas(data)

    with self.open(path, "w") as f:
        data.write_csv(f, **kwargs)


def write_file(
    self,
    data: pl.DataFrame | pl.LazyFrame | pa.Table | pd.DataFrame | dict | list[dict],
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
    mode: str = "append",  # append, overwrite, delete_matching, error_if_exists
    use_threads: bool = True,
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
        mode: (str, optional) Write mode. Defaults to 'append'. Options: 'append', 'overwrite', 'delete_matching',
            'error_if_exists'.
        use_threads: (bool, optional) If True, use parallel processing. Defaults to True.
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
        data = [data]

    if format is None:
        format = (
            path[0].split(".")[-1]
            if isinstance(path, list) and "." in path[0]
            else path.split(".")[-1] if "." in path else "parquet"
        )

    if isinstance(path, str):
        path = [path]

    def _write(i, data, p, basename):
        if f".{format}" not in p:
            if not basename:
                basename = f"data-{dt.datetime.now().strftime('%Y%m%d_%H%M%S%f')[:-3]}-{uuid.uuid4().hex[:16]}"
            p = f"{p}/{basename}-{i}.{format}"
        if mode == "delete_matching":
            write_file(self, data[i], p, format, **kwargs)
        elif mode == "overwrite":
            self.fs.rm(posixpath.dirname(p), recursive=True)
            write_file(self, data[i], p, format, **kwargs)
        elif mode == "append":
            if not self.exists(p):
                write_file(self, data[i], p, format, **kwargs)
            else:
                p = p.replace(f".{format}", f"-{i}.{format}")
                write_file(self, data[i], p, format, **kwargs)
        elif mode == "error_if_exists":
            if self.exists(p):
                raise FileExistsError(f"File already exists: {p}")
            else:
                write_file(self, data[i], p, format, **kwargs)

    if use_threads:
        run_parallel(_write, range(len(path)), data, path, basename)
    else:
        for i, p in enumerate(path):
            _write(i, data, p)


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
        **kwargs: Additional keyword arguments for `pds.write_dataset`.

    Returns:
        (list[pq.FileMetaData] | None): List of Parquet file metadata or None.
    """
    if isinstance(data, dict):
        data = _dict_to_dataframe(data)
    if isinstance(data, list):
        if isinstance(data[0], dict):
            data = _dict_to_dataframe(data)

    if not isinstance(data, list):
        data = [data]

    if isinstance(data[0], pl.LazyFrame):
        data = [dd.collect() for dd in data]

    if isinstance(data[0], pl.DataFrame):
        if concat:
            data = pl.concat(data, how="diagonal_relaxed").to_arrow()
            data = data.cast(convert_large_types_to_standard(data.schema))
        else:
            data = [dd.to_arrow() for dd in data]
            data = [dd.cast(convert_large_types_to_standard(dd.schema)) for dd in data]

    elif isinstance(data[0], pd.DataFrame):
        data = [pa.Table.from_pandas(dd, preserve_index=False) for dd in data]
        if concat:
            data = pa.concat_tables(data, promote_options="permissive")
    elif isinstance(data[0], pa.RecordBatch | pa.RecordBatchReader | Generator):
        if concat:
            data = pa.Table.from_batches(data)
        else:
            data = [pa.Table.from_batches([dd]) for dd in data]

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
    if isinstance(data, dict):
        data = _dict_to_dataframe(data)
    if isinstance(data, list):
        if isinstance(data[0], dict):
            data = _dict_to_dataframe(data)

    if not isinstance(data, list):
        data = [data]

    if isinstance(data[0], pl.LazyFrame):
        data = [dd.collect() for dd in data]

    if isinstance(data[0], pl.DataFrame):
        if concat:
            data = pl.concat(data, how="diagonal_relaxed").to_arrow()
            data = data.cast(convert_large_types_to_standard(data.schema))
        else:
            data = [dd.to_arrow() for dd in data]
            data = [dd.cast(convert_large_types_to_standard(dd.schema)) for dd in data]

    elif isinstance(data[0], pd.DataFrame):
        data = [pa.Table.from_pandas(dd, preserve_index=False) for dd in data]
        if concat:
            data = pa.concat_tables(data, promote_options="permissive")
    elif isinstance(data[0], pa.RecordBatch | pa.RecordBatchReader | Generator):
        if concat:
            data = pa.Table.from_batches(data)
        else:
            data = [pa.Table.from_batches([dd]) for dd in data]

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
AbstractFileSystem.write_pyarrow_dataset = write_pyarrow_dataset
AbstractFileSystem.write_pydala_dataset = write_pydala_dataset
