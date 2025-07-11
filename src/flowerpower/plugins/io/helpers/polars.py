import numpy as np
import polars as pl
import polars.selectors as cs

from .datetime import get_timedelta_str, get_timestamp_column

# Pre-compiled regex patterns (identical to original)
INTEGER_REGEX = r"^[-+]?\d+$"
FLOAT_REGEX = r"^[-+]?(?:\d*[.,])?\d+(?:[eE][-+]?\d+)?$"
BOOLEAN_REGEX = r"^(true|false|1|0|yes|ja|no|nein|t|f|y|j|n)$"
BOOLEAN_TRUE_REGEX = r"^(true|1|yes|ja|t|y|j)$"
DATETIME_REGEX = (
    r"^("
    r"\d{4}-\d{2}-\d{2}"  # ISO: 2023-12-31
    r"|"
    r"\d{2}/\d{2}/\d{4}"  # US: 12/31/2023
    r"|"
    r"\d{2}\.\d{2}\.\d{4}"  # German: 31.12.2023
    r"|"
    r"\d{8}"  # Compact: 20231231
    r")"
    r"([ T]\d{2}:\d{2}(:\d{2}(\.\d{1,6})?)?)?"  # Optional time: 23:59[:59[.123456]]
    r"([+-]\d{2}:?\d{2}|Z)?"  # Optional timezone: +01:00, -0500, Z
    r"$"
)

# Float32 range limits
F32_MIN = float(np.finfo(np.float32).min)
F32_MAX = float(np.finfo(np.float32).max)


def _clean_string_expr(col_name: str) -> pl.Expr:
    """Create expression to clean string values."""
    return (
        pl.col(col_name).str.strip_chars().replace({"-": None, "": None, "None": None})
    )


def _can_downcast_to_float32(series: pl.Series) -> bool:
    """Check if float values are within Float32 range."""
    finite_values = series.filter(series.is_finite())
    if finite_values.is_empty():
        return True

    min_val, max_val = finite_values.min(), finite_values.max()
    return F32_MIN <= min_val <= max_val <= F32_MAX


def _optimize_numeric_column(series: pl.Series, col_name: str, shrink: bool) -> pl.Expr:
    """Optimize numeric column types."""
    if not shrink:
        return pl.col(col_name)

    if series.dtype == pl.Float64 and not _can_downcast_to_float32(series):
        return pl.col(col_name)

    return pl.col(col_name).shrink_dtype()


def _optimize_string_column(
    series: pl.Series,
    col_name: str,
    shrink_numerics: bool,
    time_zone: str | None = None,
) -> pl.Expr:
    """Convert string column to appropriate type based on content analysis."""
    # Return early for empty or null-only series
    cleaned_expr = _clean_string_expr(col_name)
    non_null = series.drop_nulls().replace({"-": None, "": None, "None": None})
    if len(non_null) == 0:
        return pl.col(col_name).cast(series.dtype)

    stripped = non_null.str.strip_chars()
    lowercase = stripped.str.to_lowercase()

    # Check for boolean values
    if lowercase.str.contains(BOOLEAN_REGEX).all(ignore_nulls=False):
        return (
            cleaned_expr.str.to_lowercase()
            .str.contains(BOOLEAN_TRUE_REGEX)
            .alias(col_name)
        )

    elif stripped.str.contains(INTEGER_REGEX).all(ignore_nulls=False):
        int_expr = cleaned_expr.cast(pl.Int64)
        return (
            int_expr.shrink_dtype().alias(col_name)
            if shrink_numerics
            else int_expr.alias(col_name)
        )

    # Check for numeric values
    elif stripped.str.contains(FLOAT_REGEX).all(ignore_nulls=False):
        float_expr = cleaned_expr.str.replace_all(",", ".").cast(pl.Float64)

        if shrink_numerics:
            # Check if values can fit in Float32
            temp_floats = stripped.str.replace_all(",", ".").cast(
                pl.Float64, strict=False
            )
            if _can_downcast_to_float32(temp_floats):
                return float_expr.shrink_dtype().alias(col_name)

        return float_expr.alias(col_name)

    try:
        if stripped.str.contains(DATETIME_REGEX).all(ignore_nulls=False):
            return cleaned_expr.str.to_datetime(
                strict=False, time_unit="us", time_zone=time_zone
            ).alias(col_name)
    except pl.exceptions.PolarsError:
        pass

    # Keep original if no conversion applies
    return pl.col(col_name)


def _get_column_expr(
    df: pl.DataFrame, col_name: str, shrink_numerics: bool, time_zone: str | None = None
) -> pl.Expr:
    """Generate optimization expression for a single column."""
    series = df[col_name]

    # Handle all-null columns
    if series.is_null().all():
        return pl.col(col_name).cast(series.dtype)

    # Process based on current type
    if series.dtype.is_numeric():
        return _optimize_numeric_column(series, col_name, shrink_numerics)
    elif series.dtype == pl.Utf8:
        return _optimize_string_column(series, col_name, shrink_numerics, time_zone)

    # Keep original for other types
    return pl.col(col_name)


def opt_dtype(
    df: pl.DataFrame,
    include: str | list[str] | None = None,
    exclude: str | list[str] | None = None,
    time_zone: str | None = None,
    shrink_numerics: bool = True,
    strict: bool = False,
) -> pl.DataFrame:
    """
    Optimize data types of a Polars DataFrame for performance and memory efficiency.

    This function analyzes each column and converts it to the most appropriate
    data type based on content, handling string-to-type conversions and
    numeric type downcasting.

    Args:
        df: DataFrame to optimize
        include: Column(s) to include in optimization (default: all columns)
        exclude: Column(s) to exclude from optimization
        time_zone: Optional time zone for datetime parsing
        shrink_numerics: Whether to downcast numeric types when possible
        strict: If True, will raise an error if any column cannot be optimized

    Returns:
        DataFrame with optimized data types
    """
    # Normalize include/exclude parameters
    if isinstance(include, str):
        include = [include]
    if isinstance(exclude, str):
        exclude = [exclude]

    # Determine columns to process
    cols_to_process = df.columns
    if include:
        cols_to_process = [col for col in include if col in df.columns]
    if exclude:
        cols_to_process = [col for col in cols_to_process if col not in exclude]

    # Generate optimization expressions for all columns
    expressions = []
    for col_name in cols_to_process:
        try:
            expressions.append(
                _get_column_expr(df, col_name, shrink_numerics, time_zone)
            )
        except Exception as e:
            if strict:
                raise e
            # If strict mode is off, just keep the original column
            continue

    # Apply all transformations at once if any exist
    return df if not expressions else df.with_columns(expressions)


# def opt_dtype(
#     df: pl.DataFrame,
#     include: str | list[str] | None = None,
#     exclude: str | list[str] | None = None,
#     time_zone: str | None = None,
#     shrink_numerics: bool = True,
# ) -> pl.DataFrame:
#     """
#     Analyzes and optimizes the data types of a Polars DataFrame for performance
#     and memory efficiency.

#     This version includes:
#     - Robust numeric, boolean, and datetime casting from strings.
#     - Handling of whitespace and common null-like string values.
#     - Casting of columns containing only nulls to pl.Int8.
#     - Optional shrinking of numeric columns to the smallest possible type.

#     Args:
#         df: The DataFrame to optimize.
#         include: A list of columns to forcefully include in the optimization.
#         exclude: A list of columns to exclude from the optimization.
#         time_zone: Optional time zone for datetime parsing.
#         shrink_numerics: If True, numeric columns (both existing and newly converted from strings)
#             will be downcast to the smallest possible type that can hold their values (e.g., Int64 to Int32, Float64 to Float32),
#             similar to Polars' shrink_dtype() behavior. If False, this shrinking step is skipped.

#     Returns:
#         An optimized Polars DataFrame with improved data types.
#     """
#     # Phase 1: Analysis - Determine columns to process and build a list of
#     # transformation expressions without executing them immediately.
#     if isinstance(include, str):
#         include = [include]
#     if isinstance(exclude, str):
#         exclude = [exclude]

#     cols_to_process = df.columns
#     if include:
#         cols_to_process = [col for col in include if col in df.columns]
#     if exclude:
#         cols_to_process = [col for col in cols_to_process if col not in exclude]

#     expressions = []
#     for col_name in cols_to_process:
#         s = df[col_name]

#         # NEW: If a column is entirely null, cast it to Int8 and skip other checks.
#         if s.is_null().all():
#             expressions.append(pl.col(col_name).cast(pl.Int8))
#             continue

#         dtype = s.dtype

#         # 1. Optimize numeric columns by shrinking their size
#         if dtype.is_numeric():
#             if shrink_numerics:
#                 if dtype == pl.Float64:
#                     column_series = df[col_name]
#                     finite_values_series = column_series.filter(
#                         column_series.is_finite()
#                     )
#                     can_shrink = True
#                     if not finite_values_series.is_empty():
#                         min_finite_val = finite_values_series.min()
#                         max_finite_val = finite_values_series.max()
#                         if (min_finite_val < F32_MIN_FINITE) or (
#                             max_finite_val > F32_MAX_FINITE
#                         ):
#                             can_shrink = False
#                     if can_shrink:
#                         expressions.append(pl.col(col_name).shrink_dtype())
#                     else:
#                         expressions.append(pl.col(col_name))
#                 else:
#                     expressions.append(pl.col(col_name).shrink_dtype())
#             else:
#                 expressions.append(pl.col(col_name))
#             continue

#         # 2. Optimize string columns by casting to more specific types
#         if dtype == pl.Utf8:
#             # Create a cleaned column expression that first strips whitespace, then
#             # replaces common null-like strings.
#             cleaned_col = (
#                 pl.col(col_name)
#                 .str.strip_chars()
#                 .replace({"-": None, "": None, "None": None})
#             )

#             # Analyze a stripped, non-null version of the series to decide the cast type
#             s_non_null = s.drop_nulls()
#             if len(s_non_null) == 0:
#                 # The column only contains nulls or null-like strings.
#                 # Cast to Int8 as requested for all-null columns.
#                 expressions.append(pl.col(col_name).cast(pl.Int8))
#                 continue

#             s_stripped_non_null = s_non_null.str.strip_chars()

#             # Check for boolean type
#             if s_stripped_non_null.str.to_lowercase().str.contains(BOOLEAN_REGEX).all():
#                 expr = cleaned_col.str.to_lowercase().str.contains(BOOLEAN_TRUE_REGEX)
#                 expressions.append(expr.alias(col_name))
#                 continue

#             # Check for numeric type
#             if s_stripped_non_null.str.contains(NUMERIC_REGEX).all():
#                 is_float = s_stripped_non_null.str.contains(r"[.,eE]").any()
#                 numeric_col = cleaned_col.str.replace_all(",", ".")
#                 if is_float:
#                     if shrink_numerics:
#                         temp_float_series = s_stripped_non_null.str.replace_all(
#                             ",", "."
#                         ).cast(pl.Float64, strict=False)
#                         finite_values_series = temp_float_series.filter(
#                             temp_float_series.is_finite()
#                         )
#                         can_shrink = True
#                         if not finite_values_series.is_empty():
#                             min_finite_val = finite_values_series.min()
#                             max_finite_val = finite_values_series.max()
#                             if (min_finite_val < F32_MIN_FINITE) or (
#                                 max_finite_val > F32_MAX_FINITE
#                             ):
#                                 can_shrink = False
#                         base_expr = numeric_col.cast(pl.Float64)
#                         if can_shrink:
#                             expressions.append(base_expr.shrink_dtype().alias(col_name))
#                         else:
#                             expressions.append(base_expr.alias(col_name))
#                     else:
#                         expressions.append(numeric_col.cast(pl.Float64).alias(col_name))
#                 else:
#                     if shrink_numerics:
#                         expressions.append(
#                             numeric_col.cast(pl.Int64).shrink_dtype().alias(col_name)
#                         )
#                     else:
#                         expressions.append(numeric_col.cast(pl.Int64).alias(col_name))
#                 continue

#             # Check for datetime type using a fast heuristic
#             try:
#                 if s_stripped_non_null.str.contains(DATETIME_REGEX).all():
#                     expressions.append(
#                         cleaned_col.str.to_datetime(
#                             strict=False, time_unit="us", time_zone=time_zone
#                         ).alias(col_name)
#                     )
#                     continue
#             except pl.exceptions.PolarsError:
#                 pass

#     # Phase 2: Execution - If any optimizations were identified, apply them
#     # all at once for maximum parallelism and performance.
#     if not expressions:
#         return df

#     return df.with_columns(expressions)


def unnest_all(df: pl.DataFrame, seperator="_", fields: list[str] | None = None):
    def _unnest_all(struct_columns):
        if fields is not None:
            return (
                df.with_columns([
                    pl.col(col).struct.rename_fields([
                        f"{col}{seperator}{field_name}"
                        for field_name in df[col].struct.fields
                    ])
                    for col in struct_columns
                ])
                .unnest(struct_columns)
                .select(
                    list(set(df.columns) - set(struct_columns))
                    + sorted([
                        f"{col}{seperator}{field_name}"
                        for field_name in fields
                        for col in struct_columns
                    ])
                )
            )

        return df.with_columns([
            pl.col(col).struct.rename_fields([
                f"{col}{seperator}{field_name}" for field_name in df[col].struct.fields
            ])
            for col in struct_columns
        ]).unnest(struct_columns)

    struct_columns = [col for col in df.columns if df[col].dtype == pl.Struct]  # noqa: F821
    while len(struct_columns):
        df = _unnest_all(struct_columns=struct_columns)
        struct_columns = [col for col in df.columns if df[col].dtype == pl.Struct]
    return df


def explode_all(df: pl.DataFrame | pl.LazyFrame):
    list_columns = [col for col in df.columns if df[col].dtype == pl.List]
    for col in list_columns:
        df = df.explode(col)
    return df


def with_strftime_columns(
    df: pl.DataFrame | pl.LazyFrame,
    strftime: str | list[str],
    timestamp_column: str = "auto",
    column_names: str | list[str] | None = None,
):
    if timestamp_column is None or timestamp_column == "auto":
        timestamp_column = get_timestamp_column(df)
        if len(timestamp_column):
            timestamp_column = timestamp_column[0]

    if timestamp_column is None:
        raise ValueError("timestamp_column is not specified nor found in the dataframe")

    if isinstance(strftime, str):
        strftime = [strftime]
    if isinstance(column_names, str):
        column_names = [column_names]

    if column_names is None:
        column_names = [
            f"_strftime_{strftime_.replace('%', '').replace('-', '_')}_"
            for strftime_ in strftime
        ]
    # print("timestamp_column, with_strftime_columns", timestamp_column)
    return opt_dtype(
        df.with_columns([
            pl.col(timestamp_column)
            .dt.strftime(strftime_)
            .fill_null(0)
            .alias(column_name)
            for strftime_, column_name in zip(strftime, column_names)
        ]),
        include=column_names,
        strict=False,
    )


def with_truncated_columns(
    df: pl.DataFrame | pl.LazyFrame,
    truncate_by: str | list[str],
    timestamp_column: str = "auto",
    column_names: str | list[str] | None = None,
):
    if timestamp_column is None or timestamp_column == "auto":
        timestamp_column = get_timestamp_column(df)
        if len(timestamp_column):
            timestamp_column = timestamp_column[0]

        if timestamp_column is None:
            raise ValueError(
                "timestamp_column is not specified nor found in the dataframe"
            )
    if isinstance(truncate_by, str):
        truncate_by = [truncate_by]

    if isinstance(column_names, str):
        column_names = [column_names]

    if column_names is None:
        column_names = [
            f"_truncated_{truncate_.replace(' ', '_')}_" for truncate_ in truncate_by
        ]

    truncate_by = [
        get_timedelta_str(truncate_, to="polars") for truncate_ in truncate_by
    ]
    return df.with_columns([
        pl.col(timestamp_column).dt.truncate(truncate_).alias(column_name)
        for truncate_, column_name in zip(truncate_by, column_names)
    ])


def with_datepart_columns(
    df: pl.DataFrame | pl.LazyFrame,
    timestamp_column: str = "auto",
    year: bool = False,
    month: bool = False,
    week: bool = False,
    yearday: bool = False,
    monthday: bool = False,
    day: bool = False,
    weekday: bool = False,
    hour: bool = False,
    minute: bool = False,
    strftime: str | None = None,
):
    if strftime:
        if isinstance(strftime, str):
            strftime = [strftime]
        column_names = [
            f"_strftime_{strftime_.replace('%', '').replace('-', '_')}_"
            for strftime_ in strftime
        ]
    else:
        strftime = []
        column_names = []

    if year:
        strftime.append("%Y")
        column_names.append("year")
    if month:
        strftime.append("%m")
        column_names.append("month")
    if week:
        strftime.append("%W")
        column_names.append("week")
    if yearday:
        strftime.append("%j")
        column_names.append("year_day")
    if monthday:
        strftime.append("%d")
        column_names.append("day")
    if day:
        strftime.append("%d")
        column_names.append("day")
    if weekday:
        strftime.append("%a")
        column_names.append("week_day")
    if hour:
        strftime.append("%H")
        column_names.append("hour")
    if minute:
        strftime.append("%M")
        column_names.append("minute")

    column_names = [col for col in column_names if col not in df.columns]
    # print("timestamp_column, with_datepart_columns", timestamp_column)
    return with_strftime_columns(
        df=df,
        timestamp_column=timestamp_column,
        strftime=strftime,
        column_names=column_names,
    )


def with_row_count(
    df: pl.DataFrame | pl.LazyFrame,
    over: str | list[str] | None = None,
):
    if over:
        if len(over) == 0:
            over = None

    if isinstance(over, str):
        over = [over]

    if over:
        return df.with_columns(pl.lit(1).alias("row_nr")).with_columns(
            pl.col("row_nr").cum_sum().over(over)
        )
    else:
        return df.with_columns(pl.lit(1).alias("row_nr")).with_columns(
            pl.col("row_nr").cum_sum()
        )


# def delta(
#     df1: pl.DataFrame | pl.LazyFrame,
#     df2: pl.DataFrame | pl.LazyFrame,
#     subset: str | list[str] | None = None,
#     eager: bool = False,
# ) -> pl.LazyFrame:
#     columns = sorted(set(df1.columns) & set(df2.columns))

#     if subset is None:
#         subset = columns
#     if isinstance(subset, str):
#         subset = [subset]

#     subset = sorted(set(columns) & set(subset))

#     if isinstance(df1, pl.LazyFrame) and isinstance(df2, pl.DataFrame):
#         df2 = df2.lazy()

#     elif isinstance(df1, pl.DataFrame) and isinstance(df2, pl.LazyFrame):
#         df1 = df1.lazy()

#     df = (
#         pl.concat(
#             [
#                 df1.select(columns)
#                 .with_columns(pl.lit(1).alias("df"))
#                 .with_row_count(),
#                 df2.select(columns)
#                 .with_columns(pl.lit(2).alias("df"))
#                 .with_row_count(),
#             ],
#             how="vertical_relaxed",
#         )
#         .filter((pl.count().over(subset) == 1) & (pl.col("df") == 1))
#         .select(pl.exclude(["df", "row_nr"]))
#     )

#     if eager and isinstance(df, pl.LazyFrame):
#         return df.collect()
#     return df


def drop_null_columns(df: pl.DataFrame | pl.LazyFrame) -> pl.DataFrame | pl.LazyFrame:
    """Remove columns with all null values from the DataFrame."""
    return df.select([col for col in df.columns if df[col].null_count() < df.height])


def unify_schemas(dfs: list[pl.DataFrame | pl.LazyFrame]) -> pl.Schema:
    df = pl.concat([df.lazy() for df in dfs], how="diagonal_relaxed")
    if isinstance(df, pl.LazyFrame):
        return df.collect_schema()
    return df.schema


def cast_relaxed(
    df: pl.DataFrame | pl.LazyFrame, schema: pl.Schema
) -> pl.DataFrame | pl.LazyFrame:
    if isinstance(df, pl.LazyFrame):
        columns = df.collect_schema().names()
    else:
        columns = df.schema.names()
    new_columns = [col for col in schema.names() if col not in columns]
    if len(new_columns):
        return df.with_columns([
            pl.lit(None).alias(new_col) for new_col in new_columns
        ]).cast(schema)
    return df.cast(schema)


def delta(
    df1: pl.DataFrame | pl.LazyFrame,
    df2: pl.DataFrame | pl.LazyFrame,
    subset: list[str] | None = None,
    eager: bool = False,
) -> pl.DataFrame:
    s1 = df1.select(~cs.by_dtype(pl.Null())).collect_schema()
    s2 = df2.select(~cs.by_dtype(pl.Null())).collect_schema()

    columns = sorted(set(s1.names()) & set(s2.names()))

    if subset is None:
        subset = df1.columns
    if isinstance(subset, str):
        subset = [subset]

    subset = sorted(set(columns) & set(subset))

    if isinstance(df1, pl.LazyFrame) and isinstance(df2, pl.DataFrame):
        df2 = df2.lazy()

    elif isinstance(df1, pl.DataFrame) and isinstance(df2, pl.LazyFrame):
        df1 = df1.lazy()

    # cast to equal schema
    unified_schema = unify_schemas([df1.select(subset), df2.select(subset)])

    df1 = df1.cast_relaxed(unified_schema)
    df2 = df2.cast_relaxed(unified_schema)

    df = df1.join(df2, on=subset, how="anti", join_nulls=True)

    if eager and isinstance(df, pl.LazyFrame):
        return df.collect()

    return df


def partition_by(
    df: pl.DataFrame | pl.LazyFrame,
    timestamp_column: str | None = None,
    columns: str | list[str] | None = None,
    strftime: str | list[str] | None = None,
    timedelta: str | list[str] | None = None,
    num_rows: int | None = None,
) -> list[tuple[dict, pl.DataFrame | pl.LazyFrame]]:
    if columns is not None:
        if isinstance(columns, str):
            columns = [columns]
        columns_ = columns.copy()
    else:
        columns_ = []

    drop_columns = columns_.copy()

    if strftime is not None:
        if isinstance(strftime, str):
            strftime = [strftime]

        df = df.with_strftime_columns(
            timestamp_column=timestamp_column, strftime=strftime
        )
        strftime_columns = [
            f"_strftime_{strftime_.replaace('%', '')}_" for strftime_ in strftime
        ]
        columns_ += strftime_columns
        drop_columns += strftime_columns

    if timedelta is not None:
        if isinstance(timedelta, str):
            timedelta = [timedelta]

        df = df.with_duration_columns(
            timestamp_column=timestamp_column, timedelta=timedelta
        )
        timedelta_columns = [f"_timedelta_{timedelta_}_" for timedelta_ in timedelta]
        columns_ += timedelta_columns
        drop_columns += timedelta_columns

    if columns_:
        # datetime_columns = {
        #     col: col in [col.lower() for col in columns_]
        #     for col in [
        #         "year",
        #         "month",
        #         "week",
        #         "yearday",
        #         "monthday",
        #         "weekday",
        #         "strftime",
        #     ]
        #     if col not in [table_col.lower() for table_col in df.columns]
        # }
        datetime_columns = [
            col.lower()
            for col in columns_
            if col
            in [
                "year",
                "month",
                "week",
                "yearday",
                "monthday",
                "weekday",
                "day",
                "hour",
                "minute",
                "strftime",
            ]
            and col not in df.columns
        ]

        datetime_columns = {
            col: col in datetime_columns
            for col in [
                "year",
                "month",
                "week",
                "yearday",
                "monthday",
                "weekday",
                "day",
                "hour",
                "minute",
                "strftime",
            ]
        }
        if any(datetime_columns.values()):
            df = df.with_datepart_columns(
                timestamp_column=timestamp_column, **datetime_columns
            )

        if isinstance(df, pl.LazyFrame):
            df = df.collect()
        columns_ = [col for col in columns_ if col in df.columns]

    if num_rows is not None:
        df = df.with_row_count_ext(over=columns_).with_columns(
            (pl.col("row_nr") - 1) // num_rows
        )
        columns_ += ["row_nr"]
        drop_columns += ["row_nr"]

    if columns_:
        partitions = [
            (p.select(columns_).unique().to_dicts()[0], p.drop(drop_columns))
            for p in df.partition_by(
                by=columns_,
                as_dict=False,
                maintain_order=True,
            )
        ]

        return partitions

    return [({}, df)]


pl.DataFrame.unnest_all = unnest_all
pl.DataFrame.explode_all = explode_all
pl.DataFrame.opt_dtype = opt_dtype
pl.DataFrame.with_row_count_ext = with_row_count
pl.DataFrame.with_datepart_columns = with_datepart_columns
pl.DataFrame.with_duration_columns = with_truncated_columns
pl.DataFrame.with_strftime_columns = with_strftime_columns
pl.DataFrame.cast_relaxed = cast_relaxed
pl.DataFrame.delta = delta
pl.DataFrame.partition_by_ext = partition_by
pl.DataFrame.drop_null_columns = drop_null_columns

pl.LazyFrame.unnest_all = unnest_all
pl.LazyFrame.explode_all = explode_all
pl.LazyFrame.opt_dtype = opt_dtype
pl.LazyFrame.with_row_count_ext = with_row_count
pl.LazyFrame.with_datepart_columns = with_datepart_columns
pl.LazyFrame.with_duration_columns = with_truncated_columns
pl.LazyFrame.with_strftime_columns = with_strftime_columns
pl.LazyFrame.delta = delta
pl.LazyFrame.cast_relaxed = cast_relaxed
pl.LazyFrame.partition_by_ext = partition_by
pl.LazyFrame.drop_null_columns = drop_null_columns
