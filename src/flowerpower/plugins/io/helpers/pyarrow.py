import calendar
import re
from datetime import datetime, timezone

import dateutil.parser
import numpy as np
import polars as pl
import pyarrow as pa
import pyarrow.compute as pc
from dateutil import tz

F32_MIN_FINITE = np.finfo(np.float32).min
F32_MAX_FINITE = np.finfo(np.float32).max


def _try_shrink_integer_array(arr: pa.Array, shrink_numerics: bool) -> pa.Array:
    """
    Downcast a PyArrow integer array to the smallest possible integer type if shrink_numerics is True.
    """
    if not shrink_numerics:
        return arr

    if arr.null_count == len(arr):
        # All nulls, return as is (or int8)
        try:
            return pa.array([None] * len(arr), type=pa.int8())
        except Exception:
            return arr

    minmax = pc.min_max(arr)
    min_val = minmax["min"].as_py()
    max_val = minmax["max"].as_py()

    # If all values are null, min_val and max_val will be None
    if min_val is None and max_val is None:
        try:
            return pa.array([None] * len(arr), type=pa.int8())
        except Exception:
            return arr

    candidates = []
    if min_val is not None and min_val >= 0:
        candidates = [
            pa.uint8(),
            pa.int8(),
            pa.uint16(),
            pa.int16(),
            pa.uint32(),
            pa.int32(),
            pa.int64(),
        ]
    else:
        candidates = [pa.int8(), pa.int16(), pa.int32(), pa.int64()]

    for typ in candidates:
        try:
            if pa.types.is_unsigned_integer(typ):
                tmin, tmax = 0, 2 ** (typ.bit_width) - 1
            else:
                tmin, tmax = -(2 ** (typ.bit_width - 1)), 2 ** (typ.bit_width - 1) - 1
            if min_val >= tmin and max_val <= tmax:
                return pc.cast(arr, typ)
        except (pa.ArrowInvalid, pa.ArrowTypeError):
            continue
    return arr


def _try_shrink_float64_array(arr: pa.Array, shrink_numerics: bool) -> pa.Array:
    """
    Downcast a PyArrow float64 array to float32 if possible and shrink_numerics is True.
    """
    if not shrink_numerics or not pa.types.is_float64(arr.type):
        return arr

    # Filter for finite values using PyArrow compute functions
    try:
        # Ensure 'arr' is not all nulls before attempting pc.is_finite, which might error on all-null arrays
        if arr.null_count == len(arr):
            # If all nulls, can attempt to cast to float32 as it doesn't affect nulls
            try:
                return pc.cast(arr, pa.float32())
            except (pa.ArrowInvalid, TypeError):
                return arr

        finite_mask = pc.is_finite(arr)
        finite_values_arr = arr.filter(finite_mask)
    except (pa.ArrowInvalid, pa.ArrowTypeError):
        return arr

    if (
        len(finite_values_arr) == 0
    ):  # All values were non-finite, or filter resulted in empty
        try:
            # Attempt to cast original array to float32
            return pc.cast(arr, pa.float32())
        except (pa.ArrowInvalid, TypeError):
            return arr  # Fallback if cast fails

    min_max_struct = pc.min_max(finite_values_arr)
    min_val_scalar = min_max_struct["min"]
    max_val_scalar = min_max_struct["max"]

    # if pc.is_null(min_val_scalar) or pc.is_null(max_val_scalar): # Should not happen if len(finite_values_arr) > 0 and they are finite
    #    try:
    #        return pc.cast(arr, pa.float32())
    #    except (pa.ArrowInvalid, TypeError):
    #        return arr

    min_val = min_val_scalar.as_py()
    max_val = max_val_scalar.as_py()

    if (
        F32_MIN_FINITE <= min_val <= F32_MAX_FINITE
        and F32_MIN_FINITE <= max_val <= F32_MAX_FINITE
    ):
        try:
            return pc.cast(arr, pa.float32())
        except (pa.ArrowInvalid, TypeError):
            return arr  # Fallback if cast fails for other reasons
    else:
        return arr  # Values are out of float32 range


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


def to_datetime(
    arr: pa.Array,
    format: str | None = None,
    strict: bool = False,
    time_zone: str | None = None,
) -> pa.Array:
    """
    Convert a PyArrow array of strings to a datetime array.

    Args:
        arr (pa.Array): The input PyArrow array of strings.
        format (str | None): The datetime format string. If None, the format will be detected.
        strict (bool): If True, raises an error if any value cannot be parsed.
        time_zone (str | None): The timezone to use for the datetime values. If None, no timezone is applied.

    Returns:
        pa.Array: A new PyArrow array with datetime values.
    """

    def detect_datetime_format(arr):
        """
        Detect the common datetime format for a PyArrow string array.

        Args:
            arr: PyArrow string array with datetime-like strings

        Returns:
            The detected format string or None if no format could be determined
        """
        # Find the first non-null value
        sample = None
        for i in range(len(arr)):
            if arr[i] is not None:
                val = arr[i].as_py()
                if val and isinstance(val, str):
                    sample = val
                    break

        if not sample:
            return None

        # Group similar formats into families and order by specificity (most detailed first)
        format_families = {
            "iso_datetime": [
                # ISO datetime with timezone
                (
                    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:?\d{2}$",
                    "%Y-%m-%dT%H:%M:%S.%f%z",
                ),
                (
                    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:?\d{2}$",
                    "%Y-%m-%dT%H:%M:%S%z",
                ),
                (
                    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$",
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                ),
                (r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", "%Y-%m-%dT%H:%M:%SZ"),
                # ISO datetime without timezone
                (r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+$", "%Y-%m-%dT%H:%M:%S.%f"),
                (r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", "%Y-%m-%dT%H:%M:%S"),
                (r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$", "%Y-%m-%dT%H:%M"),
            ],
            "space_datetime": [
                # Datetime with space separator and timezone
                (
                    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:?\d{2}$",
                    "%Y-%m-%d %H:%M:%S.%f%z",
                ),
                (
                    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[+-]\d{2}:?\d{2}$",
                    "%Y-%m-%d %H:%M:%S%z",
                ),
                # Datetime with space separator without timezone
                (r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+$", "%Y-%m-%d %H:%M:%S.%f"),
                (r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", "%Y-%m-%d %H:%M:%S"),
                (r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$", "%Y-%m-%d %H:%M"),
            ],
            "iso_date": [
                # ISO date only
                (r"^\d{4}-\d{2}-\d{2}$", "%Y-%m-%d"),
            ],
            "us_datetime": [
                # US datetime formats
                (
                    r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2}\.\d+ [AP]M$",
                    "%m/%d/%Y %I:%M:%S.%f %p",
                ),
                (
                    r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M$",
                    "%m/%d/%Y %I:%M:%S %p",
                ),
                (r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [AP]M$", "%m/%d/%Y %I:%M %p"),
                (r"^\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}:\d{2}$", "%m/%d/%Y %H:%M:%S"),
                (r"^\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}$", "%m/%d/%Y %H:%M"),
                (r"^\d{1,2}/\d{1,2}/\d{4}$", "%m/%d/%Y"),
            ],
            "euro_datetime": [
                # European datetime formats
                (r"^\d{1,2}\.\d{1,2}\.\d{4} \d{2}:\d{2}:\d{2}$", "%d.%m.%Y %H:%M:%S"),
                (r"^\d{1,2}\.\d{1,2}\.\d{4} \d{2}:\d{2}$", "%d.%m.%Y %H:%M"),
                (r"^\d{1,2}\.\d{1,2}\.\d{4}$", "%d.%m.%Y"),
                (r"^\d{1,2}-\d{1,2}-\d{4} \d{2}:\d{2}:\d{2}$", "%d-%m-%Y %H:%M:%S"),
                (r"^\d{1,2}-\d{1,2}-\d{4} \d{2}:\d{2}$", "%d-%m-%Y %H:%M"),
                (r"^\d{1,2}-\d{1,2}-\d{4}$", "%d-%m-%Y"),
            ],
            "month_name": [
                # Month name formats
                (r"^\d{1,2} [A-Za-z]{3} \d{4} \d{2}:\d{2}:\d{2}$", "%d %b %Y %H:%M:%S"),
                (r"^\d{1,2} [A-Za-z]{3} \d{4} \d{2}:\d{2}$", "%d %b %Y %H:%M"),
                (r"^\d{1,2} [A-Za-z]{3} \d{4}$", "%d %b %Y"),
                (
                    r"^[A-Za-z]{3} \d{1,2}, \d{4} \d{2}:\d{2}:\d{2}$",
                    "%b %d, %Y %H:%M:%S",
                ),
                (r"^[A-Za-z]{3} \d{1,2}, \d{4} \d{2}:\d{2}$", "%b %d, %Y %H:%M"),
                (r"^[A-Za-z]{3} \d{1,2}, \d{4}$", "%b %d, %Y"),
                (
                    r"^[A-Za-z]{3,9} \d{1,2}, \d{4} \d{2}:\d{2}:\d{2}$",
                    "%B %d, %Y %H:%M:%S",
                ),
                (r"^[A-Za-z]{3,9} \d{1,2}, \d{4} \d{2}:\d{2}$", "%B %d, %Y %H:%M"),
                (r"^[A-Za-z]{3,9} \d{1,2}, \d{4}$", "%B %d, %Y"),
            ],
            "timestamp": [
                # Timestamp
                (r"^\d{10}$", "epoch"),  # Unix timestamp (seconds)
                (r"^\d{13}$", "epoch_ms"),  # Unix timestamp (milliseconds)
            ],
        }

        # First, try to match exact patterns
        for family, patterns in format_families.items():
            for pattern, fmt in patterns:
                if re.match(pattern, sample):
                    if fmt in ("epoch", "epoch_ms"):
                        return fmt, family

                    try:
                        datetime.strptime(sample, fmt)
                        return fmt, family
                    except ValueError:
                        continue

        # If no exact match, try component analysis
        fmt = _analyze_datetime_components(sample)
        if fmt:
            # Determine family based on format
            if "T" in fmt:
                return fmt, "iso_datetime"
            elif "%Y-%m-%d" in fmt and "T" not in fmt:
                if "%H" in fmt or "%I" in fmt:
                    return fmt, "space_datetime"
                else:
                    return fmt, "iso_date"
            elif "%m/%d/%Y" in fmt:
                return fmt, "us_datetime"
            elif "%d.%m.%Y" in fmt or "%d-%m-%Y" in fmt:
                return fmt, "euro_datetime"
            elif "%b" in fmt or "%B" in fmt:
                return fmt, "month_name"

        return None, None

    def _analyze_datetime_components(sample):
        """Analyze datetime components to build a format string."""
        if not sample:
            return None

        # Identify components
        has_date = bool(
            re.search(r"\d{1,4}[-/\.]\d{1,2}[-/\.]\d{1,4}", sample)
            or re.search(r"\d{1,2} [A-Za-z]{3,9} \d{2,4}", sample)
        )

        has_time = bool(re.search(r"\d{1,2}:\d{2}(:\d{2})?(\.\d+)?", sample))

        has_timezone = bool(
            re.search(r"[+-]\d{2}:?\d{2}$", sample)
            or re.search(r"[A-Z]{3,4}$", sample)
            or re.search(r"Z$", sample)
        )

        # Build format based on identified components
        format_parts = []

        # Date component
        if has_date:
            # Check date separator
            if "-" in sample:
                if re.search(r"^\d{4}-", sample):
                    format_parts.append("%Y-%m-%d")  # ISO format
                else:
                    format_parts.append("%d-%m-%Y")
            elif "/" in sample:
                format_parts.append("%m/%d/%Y")
            elif "." in sample:
                format_parts.append("%d.%m.%Y")
            elif re.search(r"\d{1,2} [A-Za-z]{3} \d{4}", sample):
                format_parts.append("%d %b %Y")
            elif re.search(r"\d{1,2} [A-Za-z]{3,9} \d{4}", sample):
                format_parts.append("%d %B %Y")

        # Time component
        if has_time:
            time_format = "%H:%M"
            if re.search(r":\d{2}:", sample):
                time_format = "%H:%M:%S"
            if re.search(r"\.\d+", sample):
                time_format += ".%f"
            if re.search(r"[AP]M", sample):
                time_format = time_format.replace("%H", "%I")
                time_format += " %p"

            if format_parts:
                format_parts.append(" ")
            format_parts.append(time_format)

        # Timezone component
        if has_timezone:
            if re.search(r"[+-]\d{2}:?\d{2}$", sample):
                format_parts.append("%z")
            elif re.search(r"Z$", sample):
                format_parts.append("Z")
            elif re.search(r"[A-Z]{3,4}$", sample):
                format_parts.append("%Z")

        format_string = "".join(format_parts)

        # Verify the format works for the sample
        try:
            datetime.strptime(sample, format_string)
            return format_string
        except:
            pass

        return None

    def try_parse_with_format(date_string, format_string):
        """Try to parse a date string with a given format."""
        try:
            if format_string == "epoch":
                # Handle Unix timestamp (seconds)
                timestamp = int(date_string)
                datetime.fromtimestamp(timestamp)
            elif format_string == "epoch_ms":
                # Handle Unix timestamp (milliseconds)
                timestamp = int(date_string) / 1000
                datetime.fromtimestamp(timestamp)
            else:
                datetime.strptime(date_string, format_string)
            return True
        except (ValueError, OverflowError):
            return False

    def _find_inconsistent_format_examples(
        arr, detected_format, family, max_examples=5
    ):
        """Find examples of strings that don't match the detected format family."""
        inconsistent_examples = []

        for i in range(len(arr)):
            if arr[i] is not None:
                val = arr[i].as_py()
                if val and isinstance(val, str):
                    # Try to extend the format first
                    extended_val = _try_extend_format(val, detected_format, family)
                    if (
                        extended_val != val
                    ):  # If extended, it should work with the format
                        continue

                    # If no extension was possible, check if it matches as is
                    if not try_parse_with_format(val, detected_format):
                        inconsistent_examples.append((i, val))
                        if len(inconsistent_examples) >= max_examples:
                            break

        return inconsistent_examples

    def _try_extend_format(val, detected_format, family):
        """
        Try to extend a shorter datetime string to match the detected format.
        E.g., convert '2023-01-15' to '2023-01-15 00:00:00' if the detected format is '%Y-%m-%d %H:%M:%S'

        Returns the extended string if possible, otherwise returns the original value.
        """
        # Skip non-string values or special formats
        if not isinstance(val, str) or detected_format in ("epoch", "epoch_ms"):
            return val

        # Match basic datetime components using regex
        date_match = re.match(
            r"^(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\d{1,2}\.\d{1,2}\.\d{4}|\d{1,2}-\d{1,2}-\d{4}|\d{1,2} [A-Za-z]{3} \d{4}|[A-Za-z]{3,9} \d{1,2}, \d{4})$",
            val,
        )
        datetime_match = re.match(
            r"^(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\d{1,2}\.\d{1,2}\.\d{4}|\d{1,2}-\d{1,2}-\d{4}|\d{1,2} [A-Za-z]{3} \d{4}|[A-Za-z]{3,9} \d{1,2}, \d{4}) (\d{1,2}:\d{2})$",
            val,
        )

        # Determine if extensions are needed based on the detected format and family
        if family in ["iso_date"] and "%H" in detected_format and date_match:
            # Extend date-only to include time
            if "%S" in detected_format:
                return f"{val} 00:00:00"
            else:
                return f"{val} 00:00"

        elif (
            family in ["space_datetime", "iso_datetime", "us_datetime", "euro_datetime"]
            and datetime_match
            and "%S" in detected_format
        ):
            # Extend time with no seconds to include seconds
            if ".%f" in detected_format:
                return f"{val}:00.000000"
            else:
                return f"{val}:00"

        # Handle other cases here as needed

        # No extension possible or needed
        return val

    def _expand_format(arr, detected_format, family):
        """
        Extend shorter datetime strings in the array to match the detected format.
        Returns a new array with extended values.
        """
        result = []
        for i in range(len(arr)):
            if arr[i] is not None:
                val = arr[i].as_py()
                if isinstance(val, str):
                    result.append(_try_extend_format(val, detected_format, family))
                else:
                    result.append(val)
            else:
                result.append(None)

        return pa.array(result)

    def _convert_string_array_to_datetime(
        arr, format=None, strict=True, default_timezone=None
    ):
        """
        Convert a PyArrow string array to datetime.

        Args:
            arr: PyArrow string array with datetime-like strings
            format: Optional format string to use (if None, will be auto-detected)
            strict: If False, strings that don't match the format will be set to null
                If True, will raise an exception if any strings don't match
            default_timezone: Timezone to use if the strings don't contain timezone info
                            or to convert existing timezones to

        Returns:
            PyArrow timestamp array
        """
        # Skip empty arrays
        if len(arr) == 0:
            return arr

        # Use specified format or detect it
        if format is None:
            detected_format, family = detect_datetime_format(arr)
            if not detected_format:
                raise ValueError(
                    "Could not detect datetime format. The array may be empty or contain invalid datetime strings."
                )
        else:
            detected_format = format
            # Try to determine family from format
            if "T" in format:
                family = "iso_datetime"
            elif "%Y-%m-%d" in format and "T" not in format:
                if "%H" in format or "%I" in format:
                    family = "space_datetime"
                else:
                    family = "iso_date"
            elif "%m/%d/%Y" in format:
                family = "us_datetime"
            elif "%d.%m.%Y" in format or "%d-%m-%Y" in format:
                family = "euro_datetime"
            elif "%b" in format or "%B" in format:
                family = "month_name"
            else:
                family = None

        # Try to expand shorter formats before processing
        expanded_arr = _expand_format(arr, detected_format, family)

        try:
            # Handle special formats
            if detected_format == "epoch":
                # Convert Unix timestamp (seconds) to datetime
                int_array = pa.compute.cast(expanded_arr, pa.int64())
                timestamp_array = pa.compute.multiply(int_array, 1000000).cast(
                    pa.timestamp("us")
                )

                # Apply timezone if requested
                if default_timezone:
                    timestamp_array = pa.compute.assume_timezone(
                        timestamp_array, default_timezone
                    )

                return timestamp_array

            elif detected_format == "epoch_ms":
                # Convert Unix timestamp (milliseconds) to datetime
                int_array = pa.compute.cast(expanded_arr, pa.int64())
                timestamp_array = pa.compute.multiply(int_array, 1000).cast(
                    pa.timestamp("us")
                )

                # Apply timezone if requested
                if default_timezone:
                    timestamp_array = pa.compute.assume_timezone(
                        timestamp_array, default_timezone
                    )

                return timestamp_array

            # For standard formats
            if strict:
                # In strict mode, use strptime directly and let it raise errors for mismatches
                try:
                    timestamp_array = pa.compute.strptime(
                        expanded_arr, format=detected_format, unit="us"
                    )

                    # Check if the format includes timezone information
                    has_timezone = (
                        "%z" in detected_format
                        or "%Z" in detected_format
                        or "Z" in detected_format
                    )

                    # Handle timezone conversion or addition
                    if default_timezone:
                        if has_timezone:
                            # If strings have timezone and default_timezone is specified,
                            # we need to convert to the default timezone
                            # This requires conversion to Python objects and back
                            py_datetimes = []
                            target_tz = tz.gettz(default_timezone)

                            for i in range(len(timestamp_array)):
                                if timestamp_array[i] is not None:
                                    dt = timestamp_array[i].as_py()
                                    if dt.tzinfo is not None:
                                        # Convert to target timezone
                                        dt = dt.astimezone(target_tz)
                                    py_datetimes.append(dt)
                                else:
                                    py_datetimes.append(None)

                            # Convert back to PyArrow array
                            timestamp_array = pa.array(
                                py_datetimes, type=pa.timestamp("us", default_timezone)
                            )
                        else:
                            # If strings don't have timezone, just assume the default
                            timestamp_array = pa.compute.assume_timezone(
                                timestamp_array, default_timezone
                            )

                    return timestamp_array
                except Exception as e:
                    # Find examples of inconsistent formats to help the user
                    inconsistent_examples = _find_inconsistent_format_examples(
                        arr, detected_format, family
                    )

                    if inconsistent_examples:
                        example_str = "\n".join([
                            f"  Index {idx}: '{val}'"
                            for idx, val in inconsistent_examples
                        ])
                        error_msg = (
                            f"Detected format '{detected_format}' doesn't work for all strings. "
                            f"Found inconsistent formats:\n{example_str}\n\n"
                            f"Options:\n"
                            f"1. Specify the correct format with format='{detected_format}' or another appropriate format\n"
                            f"2. Use strict=False to convert non-matching strings to null values"
                        )
                        raise ValueError(error_msg) from e
                    else:
                        raise ValueError(
                            f"Format detected as '{detected_format}' but conversion failed: {str(e)}. "
                            "Consider using strict=False."
                        ) from e
            else:
                # In non-strict mode, manually handle each value to convert mismatches to null
                values = []
                tzinfo = tz.gettz(default_timezone) if default_timezone else None

                for i in range(len(expanded_arr)):
                    if expanded_arr[i] is not None:
                        val = expanded_arr[i].as_py()
                        if val and isinstance(val, str):
                            try:
                                if detected_format == "epoch":
                                    dt = datetime.fromtimestamp(int(val))
                                    if tzinfo:
                                        dt = dt.replace(tzinfo=timezone.utc).astimezone(
                                            tzinfo
                                        )
                                    dt_value = int(
                                        calendar.timegm(dt.utctimetuple()) * 1000000
                                        + dt.microsecond
                                    )
                                    values.append(dt_value)
                                elif detected_format == "epoch_ms":
                                    dt = datetime.fromtimestamp(int(val) / 1000)
                                    if tzinfo:
                                        dt = dt.replace(tzinfo=timezone.utc).astimezone(
                                            tzinfo
                                        )
                                    dt_value = int(
                                        calendar.timegm(dt.utctimetuple()) * 1000000
                                        + dt.microsecond
                                    )
                                    values.append(dt_value)
                                else:
                                    # Try to use dateutil for more flexible parsing with timezone conversion
                                    try:
                                        dt = dateutil.parser.parse(val)

                                        # If the string has timezone and default_timezone is specified, convert
                                        if dt.tzinfo and tzinfo:
                                            dt = dt.astimezone(tzinfo)
                                        # If the string has no timezone but default_timezone is specified, assume timezone
                                        elif not dt.tzinfo and tzinfo:
                                            dt = dt.replace(tzinfo=tzinfo)

                                        # Convert to microseconds since epoch
                                        if dt.tzinfo:
                                            dt_value = int(
                                                calendar.timegm(dt.utctimetuple())
                                                * 1000000
                                                + dt.microsecond
                                            )
                                        else:
                                            dt_value = int(dt.timestamp() * 1000000)
                                        values.append(dt_value)
                                    except (ValueError, OverflowError):
                                        # Fall back to strptime
                                        dt = datetime.strptime(val, detected_format)

                                        # Handle timezone
                                        if tzinfo and not (
                                            ("%z" in detected_format)
                                            or ("%Z" in detected_format)
                                        ):
                                            dt = dt.replace(tzinfo=tzinfo)

                                        # Convert to microseconds
                                        if dt.tzinfo:
                                            dt_value = int(
                                                calendar.timegm(dt.utctimetuple())
                                                * 1000000
                                                + dt.microsecond
                                            )
                                        else:
                                            dt_value = int(dt.timestamp() * 1000000)
                                        values.append(dt_value)
                            except (ValueError, OverflowError):
                                values.append(
                                    None
                                )  # Convert to null if format doesn't match
                        else:
                            values.append(None)
                    else:
                        values.append(None)

                # Convert to timestamp array
                if default_timezone:
                    result = pa.array(values, type=pa.timestamp("us", default_timezone))
                else:
                    result = pa.array(values, type=pa.timestamp("us"))

                return result

        except Exception as e:
            if isinstance(e, ValueError) and "Options:" in str(e):
                # Pass through our custom error message
                raise
            else:
                raise ValueError(
                    f"Failed to convert array using format '{detected_format}': {str(e)}. "
                    "Consider using strict=False."
                ) from e

    return _convert_string_array_to_datetime(
        arr, format=format, strict=strict, default_timezone=time_zone
    )


# Pre-compiled regexes (from polars.py)
NUMERIC_REGEX = re.compile(r"^[-+]?[0-9]*[.,]?[0-9]+([eE][-+]?[0-9]+)?$")
INTEGER_REGEX = re.compile(r"^[-+]?\d+$")
BOOLEAN_REGEX = re.compile(
    r"^(true|false|1|0|yes|ja|no|nein|t|f|y|j|n)$", re.IGNORECASE
)
BOOLEAN_TRUE_REGEX = re.compile(r"^(true|1|yes|ja|t|y|j)$", re.IGNORECASE)
DATETIME_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}")


def opt_dtype(
    table: pa.Table,
    include: str | list[str] | None = None,
    exclude: str | list[str] | None = None,
    time_zone: str | None = None,
    shrink_numerics: bool = True,
) -> pa.Table:
    """
    Analyzes and optimizes the data types of a PyArrow Table for performance and memory efficiency.

    Args:
        table: The PyArrow Table to optimize.
        include: A list of columns to forcefully include in the optimization.
        exclude: A list of columns to exclude from the optimization.
        time_zone: Optional time zone for datetime parsing.
        shrink_numerics: If True, numeric arrays (both existing and newly converted from strings) will be downcast
            (e.g., Int64 to Int32, Float64 to Float32 if values fit). If False, this shrinking step is skipped.

    Returns:
        An optimized PyArrow Table with improved data types.
    """
    # from .pyarrow import to_datetime

    if isinstance(include, str):
        include = [include]
    if isinstance(exclude, str):
        exclude = [exclude]

    cols_to_process = table.column_names
    if include:
        cols_to_process = [col for col in include if col in table.column_names]
    if exclude:
        cols_to_process = [col for col in cols_to_process if col not in exclude]

    new_columns = []
    for col_name in table.column_names:
        arr = table[col_name]
        # Only optimize selected columns
        if col_name not in cols_to_process:
            new_columns.append(arr)
            continue

        processed_arr = arr

        # If all nulls, cast to pa.null() or pa.int8()
        if pc.all(pc.is_null(processed_arr)).as_py():
            try:
                new_columns.append(
                    pa.array([None] * len(processed_arr), type=pa.null())
                )
            except Exception:
                new_columns.append(
                    pa.array([None] * len(processed_arr), type=pa.int8())
                )
            continue

        # String columns: try to optimize
        if pa.types.is_string(processed_arr.type) or pa.types.is_large_string(
            processed_arr.type
        ):
            sample_for_regex = [v for v in processed_arr.to_pylist() if v is not None]

            # 1. Datetime detection (existing logic)
            if sample_for_regex and DATETIME_REGEX.match(str(sample_for_regex[0])):
                try:
                    new_columns.append(to_datetime(processed_arr, time_zone=time_zone))
                    continue
                except Exception:
                    pass

            # 2. Boolean detection (existing logic)
            if sample_for_regex and all(
                BOOLEAN_REGEX.match(str(v)) for v in sample_for_regex
            ):

                def str_to_bool(x):
                    if x is None:
                        return None
                    return bool(BOOLEAN_TRUE_REGEX.match(str(x)))

                bool_arr = pa.array(
                    [str_to_bool(x) for x in processed_arr.to_pylist()], type=pa.bool_()
                )
                new_columns.append(bool_arr)
                continue

            # 3. Integer detection and conversion (new logic)
            is_potentially_integer = True
            if not sample_for_regex:
                is_potentially_integer = False
            else:
                for s_val_int_check in sample_for_regex:
                    if not INTEGER_REGEX.match(str(s_val_int_check)):
                        is_potentially_integer = False
                        break

            if is_potentially_integer:
                try:
                    converted_int_arr = pc.cast(processed_arr, pa.int64())
                    shrunk_int_arr = _try_shrink_integer_array(
                        converted_int_arr, shrink_numerics
                    )
                    new_columns.append(shrunk_int_arr)
                    continue
                except (pa.ArrowInvalid, pa.ArrowTypeError, ValueError):
                    pass

            # 4. Float detection and conversion (new logic)
            is_potentially_float = True
            if not sample_for_regex:
                is_potentially_float = False
            else:
                for s_val_float_check in sample_for_regex:
                    if not NUMERIC_REGEX.match(
                        str(s_val_float_check).replace(",", ".")
                    ):
                        is_potentially_float = False
                        break

            if is_potentially_float:
                arr_dots_for_floats = processed_arr
                try:
                    arr_dots_for_floats = pc.replace_substring(
                        processed_arr, pattern=",", replacement="."
                    )
                except Exception:
                    arr_dots_for_floats = processed_arr

                try:
                    converted_float_arr = pc.cast(arr_dots_for_floats, pa.float64())
                    shrunk_float_arr = _try_shrink_float64_array(
                        converted_float_arr, shrink_numerics
                    )
                    new_columns.append(shrunk_float_arr)
                    continue
                except (pa.ArrowInvalid, pa.ArrowTypeError, ValueError):
                    try:
                        py_list_for_float = arr_dots_for_floats.to_pylist()
                        py_float_values = []
                        num_successful_conversions = 0

                        for s_val_py_float in py_list_for_float:
                            if s_val_py_float is None:
                                py_float_values.append(None)
                            else:
                                try:
                                    py_float_values.append(float(str(s_val_py_float)))
                                    num_successful_conversions += 1
                                except ValueError:
                                    py_float_values.append(None)
                        if num_successful_conversions > 0:
                            converted_float_arr_py = pa.array(
                                py_float_values, type=pa.float64()
                            )
                            shrunk_float_arr_py = _try_shrink_float64_array(
                                converted_float_arr_py, shrink_numerics
                            )
                            new_columns.append(shrunk_float_arr_py)
                            continue
                    except Exception:
                        pass

        # Shrink integer columns
        elif pa.types.is_integer(processed_arr.type):
            processed_arr = _try_shrink_integer_array(processed_arr, shrink_numerics)
            new_columns.append(processed_arr)
            continue

        # Shrink float columns
        elif pa.types.is_floating(processed_arr.type):
            if pa.types.is_float64(
                processed_arr.type
            ):  # Only attempt to shrink float64
                processed_arr = _try_shrink_float64_array(
                    processed_arr, shrink_numerics
                )
            new_columns.append(processed_arr)
            continue

        # Fallback: keep as is
        new_columns.append(processed_arr)

    return pa.table(new_columns, names=table.column_names)
