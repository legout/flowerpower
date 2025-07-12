import numpy as np
import polars as pl
import pyarrow as pa
import pyarrow.compute as pc

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


def unify_schemas(
    schemas: list[pa.Schema], use_large_dtypes: bool = False
) -> pa.Schema:
    """
    Unify a list of PyArrow schemas into a single schema.

    Args:
        schemas (list[pa.Schema]): List of PyArrow schemas to unify.

    Returns:
        pa.Schema: A unified PyArrow schema.
    """
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


def _clean_string_array(array: pa.Array) -> pa.Array:
    """
    Clean string values in a PyArrow array using vectorized operations.
    """
    if len(array) == 0 or array.null_count == len(array):
        return array

    # Trim whitespace using compute functions
    trimmed = pc.utf8_trim_whitespace(array)

    # Create mask for values to convert to null
    empty_mask = pc.equal(trimmed, "")
    dash_mask = pc.equal(trimmed, "-")
    none_mask = pc.equal(trimmed, "None")

    null_mask = pc.or_(pc.or_(empty_mask, dash_mask), none_mask)

    # Apply the mask to set matching values to null
    return pc.if_else(null_mask, None, trimmed)


def _can_downcast_to_float32(array: pa.Array) -> bool:
    """
    Check if float values are within Float32 range using vectorized operations.
    """
    if len(array) == 0 or array.null_count == len(array):
        return True

    # Use compute functions to filter finite values and calculate min/max
    is_finite = pc.is_finite(array)

    # Skip if no finite values
    if not pc.any(is_finite).as_py():
        return True

    # Filter out non-finite values
    finite_array = pc.filter(array, is_finite)

    min_val = pc.min(finite_array).as_py()
    max_val = pc.max(finite_array).as_py()

    return F32_MIN <= min_val <= max_val <= F32_MAX


def _get_optimal_int_type(array: pa.Array) -> pa.DataType:
    """
    Determine the most efficient integer type based on data range.
    """
    # Handle empty or all-null arrays
    if len(array) == 0 or array.null_count == len(array):
        return pa.int8()

    # Use compute functions to get min and max values
    min_max = pc.min_max(array)
    min_val = min_max["min"].as_py()
    max_val = min_max["max"].as_py()

    if min_val >= 0:  # Unsigned
        if max_val <= 255:
            return pa.uint8()
        elif max_val <= 65535:
            return pa.uint16()
        elif max_val <= 4294967295:
            return pa.uint32()
        else:
            return pa.uint64()
    else:  # Signed
        if -128 <= min_val and max_val <= 127:
            return pa.int8()
        elif -32768 <= min_val and max_val <= 32767:
            return pa.int16()
        elif -2147483648 <= min_val and max_val <= 2147483647:
            return pa.int32()
        else:
            return pa.int64()


def _optimize_numeric_array(array: pa.Array, shrink: bool) -> pa.Array:
    """
    Optimize numeric PyArrow array by downcasting when possible.
    Uses vectorized operations for efficiency.
    """
    if not shrink or len(array) == 0 or array.null_count == len(array):
        return array if len(array) > 0 else pa.array([], type=pa.int8())

    # Handle floating point types
    if pa.types.is_floating(array.type):
        if array.type == pa.float64() and _can_downcast_to_float32(array):
            return pc.cast(array, pa.float32())
        return array

    # Handle integer types
    if pa.types.is_integer(array.type):
        # Skip if already optimized to smallest types
        if array.type in [pa.int8(), pa.uint8()]:
            return array

        optimal_type = _get_optimal_int_type(array)
        return pc.cast(array, optimal_type)

    # Default: return unchanged
    return array


def _all_match_regex(array: pa.Array, pattern: str) -> bool:
    """
    Check if all non-null values in array match regex pattern.
    Uses pyarrow.compute.match_substring_regex for vectorized evaluation.
    """
    if len(array) == 0 or array.null_count == len(array):
        return False

    # Check if al values match the pattern
    return pc.all(pc.match_substring_regex(array, pattern, ignore_case=True)).as_py()


def _optimize_string_array(
    array: pa.Array, col_name: str, shrink_numerics: bool, time_zone: str | None = None
) -> pa.Array:
    """
    Convert string PyArrow array to appropriate type based on content analysis.
    Uses fully vectorized operations wherever possible.
    """
    # Handle empty or all-null arrays
    if len(array) == 0:
        return pa.array([], type=pa.int8())
    if array.null_count == len(array):
        return pa.array([None] * len(array), type=pa.null())

    # Clean string values
    cleaned_array = _clean_string_array(array)

    try:
        # Check for boolean values
        if _all_match_regex(cleaned_array, BOOLEAN_REGEX):
            # Match with TRUE pattern
            true_matches = pc.match_substring_regex(
                array, BOOLEAN_TRUE_REGEX, ignore_case=True
            )

            # Convert to boolean type
            return pc.cast(true_matches, pa.bool_())

        elif _all_match_regex(cleaned_array, INTEGER_REGEX):
            # Convert to integer
            # First replace commas with periods in Polars, then cast
            int_array = pc.cast(
                pc.replace_substring(cleaned_array, ",", "."), pa.int64()
            )

            if shrink_numerics:
                optimal_type = _get_optimal_int_type(int_array)
                return pc.cast(int_array, optimal_type)

            return int_array

        # Check for numeric values
        elif _all_match_regex(cleaned_array, FLOAT_REGEX):
            # Convert to float
            # First replace commas with periods in Polars
            float_array = pc.cast(
                pc.replace_substring(cleaned_array, ",", "."), pa.float64()
            )
            if shrink_numerics and _can_downcast_to_float32(float_array):
                return pc.cast(float_array, pa.float32())

            return float_array

        # Check for datetime values - use polars for conversion as specified
        elif _all_match_regex(cleaned_array, DATETIME_REGEX):
            # Convert via polars

            pl_series = pl.Series(col_name, cleaned_array)
            converted = pl_series.str.to_datetime(
                strict=False, time_unit="us", time_zone=time_zone
            )
            # Convert polars datetime back to pyarrow
            return converted.to_arrow()

    except Exception:
        # Fallback: return cleaned strings on any error
        return cleaned_array

    # Default: return cleaned strings
    return cleaned_array


def _process_column(
    table: pa.Table, col_name: str, shrink_numerics: bool, time_zone: str | None = None
) -> pa.Array:
    """
    Process a single column for type optimization.
    """
    array = table[col_name]

    # Handle all-null columns
    if array.null_count == len(array):
        return pa.array([None] * len(array), type=pa.null())

    # Process based on current type
    if pa.types.is_floating(array.type) or pa.types.is_integer(array.type):
        return _optimize_numeric_array(array, shrink_numerics)
    elif pa.types.is_string(array.type):
        return _optimize_string_array(array, col_name, shrink_numerics, time_zone)

    # Keep original for other types
    return array


def opt_dtype(
    table: pa.Table,
    include: str | list[str] | None = None,
    exclude: str | list[str] | None = None,
    time_zone: str | None = None,
    shrink_numerics: bool = True,
    strict: bool = False,
) -> pa.Table:
    """
    Optimize data types of a PyArrow Table for performance and memory efficiency.

    This function analyzes each column and converts it to the most appropriate
    data type based on content, handling string-to-type conversions and
    numeric type downcasting. It is the PyArrow equivalent of the Polars
    `opt_dtype` function.

    Args:
        table: PyArrow Table to optimize
        include: Column(s) to include in optimization (default: all columns)
        exclude: Column(s) to exclude from optimization
        time_zone: Optional time zone for datetime parsing
        shrink_numerics: Whether to downcast numeric types when possible
        strict: If True, will raise an error if any column cannot be optimized

    Returns:
        PyArrow Table with optimized data types
    """
    # Normalize include/exclude parameters
    if isinstance(include, str):
        include = [include]
    if isinstance(exclude, str):
        exclude = [exclude]

    # Determine columns to process
    cols_to_process = table.column_names
    if include:
        cols_to_process = [col for col in include if col in table.column_names]
    if exclude:
        cols_to_process = [col for col in cols_to_process if col not in exclude]

    # Process each column and build a new table
    new_columns = []
    for col_name in table.column_names:
        if col_name in cols_to_process:
            try:
                # Process column for optimization
                new_columns.append(
                    _process_column(table, col_name, shrink_numerics, time_zone)
                )
            except Exception as e:
                if strict:
                    raise e
                new_columns.append(table[col_name])
        else:
            new_columns.append(table[col_name])

    # Create a new table with the optimized columns
    return pa.Table.from_arrays(new_columns, names=table.column_names)
