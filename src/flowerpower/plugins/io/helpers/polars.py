from functools import partial

import pandas as pd
import polars as pl
import polars.selectors as cs

from .datetime import get_timedelta_str, get_timestamp_column

# import string


def unnest_all(df: pl.DataFrame, seperator="_", fields: list[str] | None = None):
    def _unnest_all(struct_columns):
        if fields is not None:
            return (
                df.with_columns(
                    [
                        pl.col(col).struct.rename_fields(
                            [
                                f"{col}{seperator}{field_name}"
                                for field_name in df[col].struct.fields
                            ]
                        )
                        for col in struct_columns
                    ]
                )
                .unnest(struct_columns)
                .select(
                    list(set(df.columns) - set(struct_columns))
                    + sorted(
                        [
                            f"{col}{seperator}{field_name}"
                            for field_name in fields
                            for col in struct_columns
                        ]
                    )
                )
            )

        return df.with_columns(
            [
                pl.col(col).struct.rename_fields(
                    [
                        f"{col}{seperator}{field_name}"
                        for field_name in df[col].struct.fields
                    ]
                )
                for col in struct_columns
            ]
        ).unnest(struct_columns)

    struct_columns = [col for col in df.columns if df[col].dtype == pl.Struct]  # noqa: F821
    while len(struct_columns):
        df = _unnest_all(struct_columns=struct_columns)
        struct_columns = [col for col in df.columns if df[col].dtype == pl.Struct]
    return df


def _opt_dtype(
    s: pl.Series, strict: bool = True, shrink_dtype: bool = True
) -> pl.Series:
    if s.dtype == pl.Utf8():
        try:
            s = s.set(s == "-", None).set(s == "", None).set(s == "None", None)

            # cast string numbers to int or float
            if (
                s.str.contains(r"^[-+]?[0-9]*[.,]?[0-9]+([eE][-+]?[0-9]+)?$")
                | s.is_null()
                | s.str.contains(r"^$")
            ).all():
                s = (
                    s.str.replace_all(",", ".")
                    # .str.replace_all("^0{1,}$", "+0")
                    # .str.strip_chars_start("0")
                    .str.replace_all(r"\.0*$", "")
                )
                s = s.set(s == "-", None).set(s == "", None).set(s == "None", None)
                if s.str.contains(r"\.").any() | s.str.contains("NaN").any():
                    s = s.cast(pl.Float64(), strict=True)
                    if shrink_dtype:
                        if s.min() >= -16777216 and s.max() <= 16777216:
                            s = s.cast(pl.Float32(), strict=True)
                else:
                    s = s.cast(pl.Int64(), strict=True)
                    if shrink_dtype:
                        s = s.shrink_dtype()

            # cast str to datetime

            elif (
                s.str.contains(r"^\d{4}-\d{2}-\d{2}$")
                | s.str.contains(r"^\d{1,2}\/\d{1,2}\/\d{4}$")
                | s.str.contains(
                    r"^\d{4}-\d{2}-\d{2}T{0,1}\s{0,1}\d{2}:\d{2}(:\d{2})?.\d{0,}$"
                )
                | s.str.contains(
                    r"^\d{4}-\d{2}-\d{2}T{0,1}\s{0,1}\d{2}:\d{2}(:\d{2})?\.\d{0,}$"
                )
                | s.str.contains(
                    r"^\d{4}-\d{2}-\d{2}T{0,1}\s{0,1}\d{2}:\d{2}(:\d{2})?\.\d{1,}\w{0,1}\+\d{0,2}:\d{0,2}:\d{0,2}$"
                )
                | s.is_null()
                | s.str.contains("^$")
            ).all():
                s = pl.Series(
                    name=s.name, values=pd.to_datetime(s, format="mixed")
                ).cast(pl.Datetime("us"))

            # cast str to bool
            elif (
                s.str.to_lowercase()
                .str.contains("^(true|false|1|0|wahr|falsch|nein|nok|ok|ja)$")
                .all()
            ):
                s = s.str.to_lowercase().str.contains(
                    "^(true|1|wahr|ja|ok)$", strict=True
                )

        except Exception as e:
            if strict:
                e.add_note(
                    "if you were trying to cast Utf8 to temporal dtypes, consider setting `strict=False`"
                )
                raise e
    else:
        if shrink_dtype:
            if s.dtype == pl.Float64():
                if s.min() >= -16777216 and s.max() <= 16777216:
                    s = s.cast(pl.Float32(), strict=True)
            else:
                s = s.shrink_dtype()

    return s


def opt_dtype(
    df: pl.DataFrame,
    exclude: str | list[str] | None = None,
    strict: bool = True,
    include: str | list[str] | None = None,
    shrink_dtype: bool = True,
) -> pl.DataFrame:
    _opt_dtype_strict = partial(_opt_dtype, strict=strict, shrink_dtype=shrink_dtype)
    _opt_dtype_not_strict = partial(_opt_dtype, strict=False, shrink_dtype=shrink_dtype)
    if include is not None:
        if isinstance(include, str):
            include = [include]
        exclude = [col for col in df.columns if col not in include]
    return (
        df.with_columns(
            pl.all()
            .exclude(exclude)
            .map_batches(_opt_dtype_strict if strict else _opt_dtype_not_strict)
        )
        if exclude is not None
        else df.with_columns(
            pl.all().map_batches(_opt_dtype_strict if strict else _opt_dtype_not_strict)
        )
    )


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
        df.with_columns(
            [
                pl.col(timestamp_column)
                .dt.strftime(strftime_)
                .fill_null(0)
                .alias(column_name)
                for strftime_, column_name in zip(strftime, column_names)
            ]
        ),
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
    return df.with_columns(
        [
            pl.col(timestamp_column).dt.truncate(truncate_).alias(column_name)
            for truncate_, column_name in zip(truncate_by, column_names)
        ]
    )


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


def unify_schema(dfs: list[pl.DataFrame | pl.LazyFrame]) -> pl.Schema:
    df = pl.concat(dfs, how="diagonal_relaxed")
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
        return df.with_columns(
            [pl.lit(None).alias(new_col) for new_col in new_columns]
        ).cast(schema)
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
    unified_schema = unify_schema([df1.select(subset), df2.select(subset)])

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

        df = df.with_striftime_columns(
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


def drop_null_columns(df: pl.DataFrame | pl.LazyFrame) -> pl.DataFrame | pl.LazyFrame:
    return df.select([col for col in df.columns if not df[col].is_null().all()])


pl.DataFrame.unnest_all = unnest_all
pl.DataFrame.explode_all = explode_all
pl.DataFrame.opt_dtype = opt_dtype
pl.DataFrame.with_row_count_ext = with_row_count
pl.DataFrame.with_datepart_columns = with_datepart_columns
pl.DataFrame.with_duration_columns = with_truncated_columns
pl.DataFrame.with_striftime_columns = with_strftime_columns
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
pl.LazyFrame.with_striftime_columns = with_strftime_columns
pl.LazyFrame.delta = delta
pl.LazyFrame.cast_relaxed = cast_relaxed
pl.LazyFrame.partition_by_ext = partition_by
pl.LazyFrame.drop_null_columns = drop_null_columns
