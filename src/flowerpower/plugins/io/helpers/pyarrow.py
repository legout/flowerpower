import concurrent.futures

import numpy as np
import polars as pl
import pyarrow as pa
import pyarrow.compute as pc

# Pre-compiled regex patterns (identical to original)
INTEGER_REGEX = r"^[-+]?\d+$"
FLOAT_REGEX = r"^[-+]?(?:\d*[.,])?\d+(?:[eE][-+]?\d+)?$"
BOOLEAN_REGEX = r"^(true|false|1|0|yes|ja|no|nein|t|f|y|j|n|ok|nok)$"
BOOLEAN_TRUE_REGEX = r"^(true|1|yes|ja|t|y|j|ok)$"
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


def dominant_timezone_per_column(
    schemas: list[pa.Schema],
) -> dict[str, tuple[str | None, str | None]]:
    """
    For each timestamp column (by name) across all schemas, detect the most frequent timezone (including None).
    If None and a timezone are tied, prefer the timezone.
    Returns a dict: {column_name: dominant_timezone}
    """
    from collections import Counter, defaultdict

    tz_counts = defaultdict(Counter)
    units = {}

    for schema in schemas:
        for field in schema:
            if pa.types.is_timestamp(field.type):
                tz = field.type.tz
                name = field.name
                tz_counts[name][tz] += 1
                # Track unit for each column (assume consistent)
                if name not in units:
                    units[name] = field.type.unit

    dominant = {}
    for name, counter in tz_counts.items():
        most_common = counter.most_common()
        if not most_common:
            continue
        top_count = most_common[0][1]
        # Find all with top_count
        top_tzs = [tz for tz, cnt in most_common if cnt == top_count]
        # If tie and one is not None, prefer not-None
        if len(top_tzs) > 1 and any(tz is not None for tz in top_tzs):
            tz = next(tz for tz in top_tzs if tz is not None)
        else:
            tz = most_common[0][0]
        dominant[name] = (units[name], tz)
    return dominant


def standardize_schema_timezones_by_majority(
    schemas: list[pa.Schema],
) -> list[pa.Schema]:
    """
    For each timestamp column (by name) across all schemas, set the timezone to the most frequent (with tie-breaking).
    Returns a new list of schemas with updated timestamp timezones.
    """
    dom = dominant_timezone_per_column(schemas)
    new_schemas = []
    for schema in schemas:
        fields = []
        for field in schema:
            if pa.types.is_timestamp(field.type) and field.name in dom:
                unit, tz = dom[field.name]
                fields.append(
                    pa.field(
                        field.name,
                        pa.timestamp(unit, tz),
                        field.nullable,
                        field.metadata,
                    )
                )
            else:
                fields.append(field)
        new_schemas.append(pa.schema(fields, schema.metadata))
    return new_schemas


def standardize_schema_timezones(
    schemas: list[pa.Schema], timezone: str | None = None
) -> list[pa.Schema]:
    """
    Standardize timezone info for all timestamp columns in a list of PyArrow schemas.

    Args:
        schemas (list of pa.Schema): List of PyArrow schemas.
        timezone (str or None): If None, remove timezone from all timestamp columns.
                                If str, set this timezone for all timestamp columns.
                                If "auto", use the most frequent timezone across schemas.

    Returns:
        list of pa.Schema: New schemas with standardized timezone info.
    """
    if timezone == "auto":
        # Use the most frequent timezone for each column
        return standardize_schema_timezones_by_majority(schemas)
    new_schemas = []
    for schema in schemas:
        fields = []
        for field in schema:
            if pa.types.is_timestamp(field.type):
                fields.append(
                    pa.field(
                        field.name,
                        pa.timestamp(field.type.unit, timezone),
                        field.nullable,
                        field.metadata,
                    )
                )
            else:
                fields.append(field)
        new_schemas.append(pa.schema(fields, schema.metadata))
    return new_schemas


def unify_schemas(
    schemas: list[pa.Schema],
    use_large_dtypes: bool = False,
    timezone: str | None = None,
    standardize_timezones: bool = True,
) -> pa.Schema:
    """
    Unify a list of PyArrow schemas into a single schema.

    Args:
        schemas (list[pa.Schema]): List of PyArrow schemas to unify.
        use_large_dtypes (bool): If True, keep large types like large_string.
        timezone (str | None): If specified, standardize all timestamp columns to this timezone.
            If "auto", use the most frequent timezone across schemas.
            If None, remove timezone from all timestamp columns.
        standardize_timezones (bool): If True, standardize all timestamp columns to the most frequent timezone.

    Returns:
        pa.Schema: A unified PyArrow schema.
    """
    if standardize_timezones:
        schemas = standardize_schema_timezones(schemas, timezone)
    try:
        return pa.unify_schemas(schemas, promote_options="permissive")
    except (pa.lib.ArrowInvalid, pa.lib.ArrowTypeError) as e:
        _ = e.args[0]
        # If unify_schemas fails, we can try to create a schema with empty tables
        schema = (
            pl.concat(
                [
                    # pl.from_arrow(pa.Table.from_pylist([], schema=schema))
                    pl.from_arrow(schema.empty_table())
                    for schema in schemas
                ],
                how="diagonal_relaxed",
            )
            .to_arrow()
            .schema
        )
        if not use_large_dtypes:
            return convert_large_types_to_normal(schema)
        return schema


def cast_schema(table: pa.Table, schema: pa.Schema) -> pa.Table:
    """
    Cast a PyArrow table to a given schema, updating the schema to match the table's columns.

    Args:
        table (pa.Table): The PyArrow table to cast.
        schema (pa.Schema): The target schema to cast the table to.

    Returns:
        pa.Table: A new PyArrow table with the specified schema.
    """
    # Filter schema fields to only those present in the table
    table_columns = set(table.schema.names)
    filtered_fields = [field for field in schema if field.name in table_columns]
    updated_schema = pa.schema(filtered_fields)
    return table.select(updated_schema.names).cast(updated_schema)


def convert_large_types_to_normal(schema: pa.Schema) -> pa.Schema:
    """
    Convert large types in a PyArrow schema to their standard types.

    Args:
        schema (pa.Schema): The PyArrow schema to convert.

    Returns:
        pa.Schema: A new PyArrow schema with large types converted to standard types.
    """
    # Define mapping of large types to standard types
    type_mapping = {
        pa.large_string(): pa.string(),
        pa.large_binary(): pa.binary(),
        pa.large_utf8(): pa.utf8(),
        pa.large_list(pa.null()): pa.list_(pa.null()),
        pa.large_list_view(pa.null()): pa.list_view(pa.null()),
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
                type=pa.list_(
                    type_mapping[field_type.value_type]
                    if field_type.value_type in type_mapping
                    else field_type.value_type
                ),
                nullable=field.nullable,
                metadata=field.metadata,
            )
            new_fields.append(new_field)
        # Handle dictionary with large_string, large_utf8, or large_binary values
        elif isinstance(field_type, pa.DictionaryType):
            new_field = pa.field(
                name=field.name,
                type=pa.dictionary(
                    field_type.index_type,
                    type_mapping[field_type.value_type]
                    if field_type.value_type in type_mapping
                    else field_type.value_type,
                    field_type.ordered,
                ),
                # nullable=field.nullable,
                metadata=field.metadata,
            )
            new_fields.append(new_field)
        else:
            new_fields.append(field)

    return pa.schema(new_fields)


def _clean_string_array(array: pa.Array) -> pa.DataType:
    """
    Clean string values in a PyArrow array using vectorized operations.
    Returns the optimal dtype after cleaning.
    """
    if len(array) == 0 or array.null_count == len(array):
        return array.type

    # Trim whitespace using compute functions
    trimmed = pc.utf8_trim_whitespace(array)

    # Create mask for values to convert to null
    empty_mask = pc.equal(trimmed, "")
    dash_mask = pc.equal(trimmed, "-")
    none_mask = pc.or_(
        pc.equal(trimmed, "None"),
        pc.equal(trimmed, "none"),
        pc.equal(trimmed, "NONE"),
        pc.equal(trimmed, "Nan"),
        pc.equal(trimmed, "N/A"),
        pc.equal(trimmed, "n/a"),
        pc.equal(trimmed, "NaN"),
        pc.equal(trimmed, "nan"),
        pc.equal(trimmed, "NAN"),
        pc.equal(trimmed, "Null"),
        pc.equal(trimmed, "NULL"),
        pc.equal(trimmed, "null"),
    )

    null_mask = pc.or_(pc.or_(empty_mask, dash_mask), none_mask)

    # If all values are null after cleaning, return null type
    if pc.all(null_mask).as_py():
        return pa.null()

    return array.type  # Default: keep string type if not all null


def _can_downcast_to_float32(array: pa.Array) -> bool:
    """
    Check if float values are within Float32 range using vectorized operations.
    """
    if len(array) == 0 or array.null_count == len(array):
        return True

    is_finite = pc.is_finite(array)
    if not pc.any(is_finite).as_py():
        return True

    finite_array = pc.filter(array, is_finite)
    min_val = pc.min(finite_array).as_py()
    max_val = pc.max(finite_array).as_py()

    return F32_MIN <= min_val <= max_val <= F32_MAX


def _get_optimal_int_type(
    array: pa.Array, allow_unsigned: bool, allow_null: bool = True
) -> pa.DataType:
    """
    Determine the most efficient integer type based on data range.
    """
    if len(array) == 0 or array.null_count == len(array):
        if allow_null:
            return pa.null()
        else:
            # If all values are null and allow_null is False, default to int8
            return pa.int8()

    min_max = pc.min_max(array)
    min_val = min_max["min"].as_py()
    max_val = min_max["max"].as_py()

    if allow_unsigned and min_val >= 0:
        if max_val <= 255:
            return pa.uint8()
        elif max_val <= 65535:
            return pa.uint16()
        elif max_val <= 4294967295:
            return pa.uint32()
        else:
            return pa.uint64()
    else:
        if -128 <= min_val and max_val <= 127:
            return pa.int8()
        elif -32768 <= min_val and max_val <= 32767:
            return pa.int16()
        elif -2147483648 <= min_val and max_val <= 2147483647:
            return pa.int32()
        else:
            return pa.int64()


def _optimize_numeric_array(
    array: pa.Array, shrink: bool, allow_unsigned: bool = True, allow_null: bool = True
) -> pa.DataType:
    """
    Optimize numeric PyArrow array by downcasting when possible.
    Returns the optimal dtype.
    """

    if not shrink or len(array) == 0 or array.null_count == len(array):
        if allow_null:
            return pa.null()
        else:
            return array.type

    if pa.types.is_floating(array.type):
        if array.type == pa.float64() and _can_downcast_to_float32(array):
            return pa.float32()
        return array.type

    if pa.types.is_integer(array.type):
        return _get_optimal_int_type(array, allow_unsigned, allow_null)

    return array.type


def _all_match_regex(array: pa.Array, pattern: str) -> bool:
    """
    Check if all non-null values in array match regex pattern.
    """
    if len(array) == 0 or array.null_count == len(array):
        return False
    return pc.all(pc.match_substring_regex(array, pattern, ignore_case=True)).as_py()


def _optimize_string_array(
    array: pa.Array,
    col_name: str,
    shrink_numerics: bool,
    time_zone: str | None = None,
    allow_unsigned: bool = True,
    allow_null: bool = True,
) -> pa.DataType:
    """
    Convert string PyArrow array to appropriate type based on content analysis.
    Returns the optimal dtype.
    """
    if len(array) == 0 or array.null_count == len(array):
        if allow_null:
            return pa.null()
        else:
            return array.type

    cleaned_array = _clean_string_array(
        array, allow_null
    )  # pc.utf8_trim_whitespace(array)

    try:
        if _all_match_regex(cleaned_array, BOOLEAN_REGEX):
            return pa.bool_()
        elif _all_match_regex(cleaned_array, INTEGER_REGEX):
            int_array = pc.cast(
                pc.replace_substring(cleaned_array, ",", "."), pa.int64()
            )
            return _optimize_numeric_array(
                int_array, allow_unsigned=allow_unsigned, allow_null=allow_null
            )
        elif _all_match_regex(cleaned_array, FLOAT_REGEX):
            float_array = pc.cast(
                pc.replace_substring(cleaned_array, ",", "."), pa.float64()
            )
            return _optimize_numeric_array(
                float_array,
                shrink_numerics,
                allow_unsigned=allow_unsigned,
                allow_null=allow_null,
            )
        elif _all_match_regex(cleaned_array, DATETIME_REGEX):
            pl_series = pl.Series(col_name, cleaned_array)
            converted = pl_series.str.to_datetime(
                strict=False, time_unit="us", time_zone=time_zone
            )
            # Get the Arrow dtype from Polars
            arrow_dtype = converted.to_arrow().type
            return arrow_dtype
    except Exception:
        return pa.string()

    return pa.string()


def _process_column(
    # table: pa.Table,
    # col_name: str,
    array: pa.Array,
    col_name: str,
    shrink_numerics: bool,
    allow_unsigned: bool,
    time_zone: str | None = None,
) -> pa.Field:
    """
    Process a single column for type optimization.
    Returns a pyarrow.Field with the optimal dtype.
    """
    # array = table[col_name]
    if array.null_count == len(array):
        return pa.field(col_name, pa.null())

    if pa.types.is_floating(array.type) or pa.types.is_integer(array.type):
        dtype = _optimize_numeric_array(array, shrink_numerics, allow_unsigned)
        return pa.field(col_name, dtype, nullable=array.null_count > 0)
    elif pa.types.is_string(array.type):
        dtype = _optimize_string_array(array, col_name, shrink_numerics, time_zone)
        return pa.field(col_name, dtype, nullable=array.null_count > 0)

    return pa.field(col_name, array.type, nullable=array.null_count > 0)


def _process_column_for_opt_dtype(args):
    (
        array,
        col_name,
        cols_to_process,
        shrink_numerics,
        allow_unsigned,
        time_zone,
        strict,
        allow_null,
    ) = args
    try:
        if col_name in cols_to_process:
            field = _process_column(
                array, col_name, shrink_numerics, allow_unsigned, time_zone
            )
            if pa.types.is_null(field.type):
                if allow_null:
                    array = pa.nulls(array.length(), type=pa.null())
                    return (col_name, field, array)
                else:
                    orig_type = array.type
                    # array = table[col_name]
                    field = pa.field(col_name, orig_type, nullable=True)
                    return (col_name, field, array)
            else:
                array = array.cast(field.type)
                return (col_name, field, array)
        else:
            field = pa.field(col_name, array.type, nullable=True)
            # array = table[col_name]
            return (col_name, field, array)
    except Exception as e:
        if strict:
            raise e
        field = pa.field(col_name, array.type, nullable=True)
        return (col_name, field, array)


def opt_dtype(
    table: pa.Table,
    include: str | list[str] | None = None,
    exclude: str | list[str] | None = None,
    time_zone: str | None = None,
    shrink_numerics: bool = True,
    allow_unsigned: bool = True,
    use_large_dtypes: bool = False,
    strict: bool = False,
    allow_null: bool = True,
) -> pa.Table:
    """
    Optimize data types of a PyArrow Table for performance and memory efficiency.
    Returns a new table casted to the optimal schema.

    Args:
        allow_null (bool): If False, columns that only hold null-like values will not be converted to pyarrow.null().
    """
    if isinstance(include, str):
        include = [include]
    if isinstance(exclude, str):
        exclude = [exclude]

    cols_to_process = table.column_names
    if include:
        cols_to_process = [col for col in include if col in table.column_names]
    if exclude:
        cols_to_process = [col for col in cols_to_process if col not in exclude]

    # Prepare arguments for parallel processing
    args_list = [
        (
            table[col_name],
            col_name,
            cols_to_process,
            shrink_numerics,
            allow_unsigned,
            time_zone,
            strict,
            allow_null,
        )
        for col_name in table.column_names
    ]

    # Parallelize column processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(_process_column_for_opt_dtype, args_list))

    # Sort results to preserve column order
    results.sort(key=lambda x: table.column_names.index(x[0]))
    fields = [field for _, field, _ in results]
    arrays = [array for _, _, array in results]

    schema = pa.schema(fields)
    if use_large_dtypes:
        schema = convert_large_types_to_normal(schema)
    return pa.Table.from_arrays(arrays, schema=schema)
