import datetime as dt
import re
from functools import lru_cache
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pyarrow as pa
import pyarrow.compute as pc
from sqlglot import exp, parse_one

from .polars import pl


@lru_cache(maxsize=128)
def timestamp_from_string(
    timestamp_str: str,
    tz: str | None = None,
    naive: bool = False,
) -> dt.datetime | dt.date | dt.time:
    """
    Converts a timestamp string (ISO 8601 format) into a datetime, date, or time object
    using only standard Python libraries.

    Handles strings with or without timezone information (e.g., '2023-01-01T10:00:00+02:00',
    '2023-01-01', '10:00:00'). Supports timezone offsets like '+HH:MM' or '+HHMM'.
    For named timezones (e.g., 'Europe/Paris'), requires Python 3.9+ and the 'tzdata'
    package to be installed.

    Args:
        timestamp_str (str): The string representation of the timestamp (ISO 8601 format).
        tz (str, optional): Target timezone identifier (e.g., 'UTC', '+02:00', 'Europe/Paris').
            If provided, the output datetime/time will be localized or converted to this timezone.
            Defaults to None.
        naive (bool, optional): If True, return a naive datetime/time (no timezone info),
            even if the input string or `tz` parameter specifies one. Defaults to False.

    Returns:
        Union[dt.datetime, dt.date, dt.time]: The parsed datetime, date, or time object.

    Raises:
        ValueError: If the timestamp string format is invalid or the timezone is
                    invalid/unsupported.
    """

    # Regex to parse timezone offsets like +HH:MM or +HHMM
    _TZ_OFFSET_REGEX = re.compile(r"([+-])(\d{2}):?(\d{2})")

    def _parse_tz_offset(tz_str: str) -> dt.tzinfo | None:
        """Parses a timezone offset string into a timezone object."""
        match = _TZ_OFFSET_REGEX.fullmatch(tz_str)
        if match:
            sign, hours, minutes = match.groups()
            offset_seconds = (int(hours) * 3600 + int(minutes) * 60) * (
                -1 if sign == "-" else 1
            )
            if abs(offset_seconds) >= 24 * 3600:
                raise ValueError(f"Invalid timezone offset: {tz_str}")
            return dt.timezone(dt.timedelta(seconds=offset_seconds), name=tz_str)
        return None

    def _get_tzinfo(tz_identifier: str | None) -> dt.tzinfo | None:
        """Gets a tzinfo object from a string (offset or IANA name)."""
        if tz_identifier is None:
            return None
        if tz_identifier.upper() == "UTC":
            return dt.timezone.utc

        # Try parsing as offset first
        offset_tz = _parse_tz_offset(tz_identifier)
        if offset_tz:
            return offset_tz

        # Try parsing as IANA name using zoneinfo (if available)
        if ZoneInfo:
            try:
                return ZoneInfo(tz_identifier)
            except ZoneInfoNotFoundError:
                raise ValueError(
                    f"Timezone '{tz_identifier}' not found. Install 'tzdata' or use offset format."
                )
            except Exception as e:  # Catch other potential zoneinfo errors
                raise ValueError(f"Error loading timezone '{tz_identifier}': {e}")
        else:
            # zoneinfo not available
            raise ValueError(
                f"Invalid timezone: '{tz_identifier}'. Use offset format (e.g., '+02:00') "
                "or run Python 3.9+ with 'tzdata' installed for named timezones."
            )

    target_tz: dt.tzinfo | None = _get_tzinfo(tz)
    parsed_obj: dt.datetime | dt.date | dt.time | None = None

    # Preprocess: Replace space separator, strip whitespace
    processed_str = timestamp_str.strip().replace(" ", "T")

    # Attempt parsing (datetime, date, time) using fromisoformat
    try:
        # Python < 3.11 fromisoformat has limitations (e.g., no Z, no +HHMM offset)
        # This implementation assumes Python 3.11+ for full ISO 8601 support via fromisoformat
        # or that input strings use formats compatible with older versions (e.g., +HH:MM)
        parsed_obj = dt.datetime.fromisoformat(processed_str)
    except ValueError:
        try:
            parsed_obj = dt.date.fromisoformat(processed_str)
        except ValueError:
            try:
                # Time parsing needs care, especially with offsets in older Python
                parsed_obj = dt.time.fromisoformat(processed_str)
            except ValueError:
                # Add fallback for simple HH:MM:SS if needed, though less robust
                # try:
                #     parsed_obj = dt.datetime.strptime(processed_str, "%H:%M:%S").time()
                # except ValueError:
                raise ValueError(f"Invalid timestamp format: '{timestamp_str}'")

    # Apply timezone logic if we have a datetime or time object
    if isinstance(parsed_obj, (dt.datetime, dt.time)):
        is_aware = (
            parsed_obj.tzinfo is not None
            and parsed_obj.tzinfo.utcoffset(
                parsed_obj if isinstance(parsed_obj, dt.datetime) else None
            )
            is not None
        )

        if target_tz:
            if is_aware:
                # Convert existing aware object to target timezone (only for datetime)
                if isinstance(parsed_obj, dt.datetime):
                    parsed_obj = parsed_obj.astimezone(target_tz)
                # else: dt.time cannot be converted without a date context. Keep original tz.
            else:
                # Localize naive object to target timezone
                parsed_obj = parsed_obj.replace(tzinfo=target_tz)
            is_aware = True  # Object is now considered aware

        # Handle naive flag: remove tzinfo if requested
        if naive and is_aware:
            parsed_obj = parsed_obj.replace(tzinfo=None)

    # If it's a date object, tz/naive flags are ignored
    elif isinstance(parsed_obj, dt.date):
        pass

    return parsed_obj


# Compile regex patterns once for efficiency
SPLIT_PATTERN = re.compile(
    r"<=|<|>=|>|=|!=|\s+[n,N][o,O][t,T]\s+[i,I][n,N]\s+|\s+[i,I][n,N]\s+|"
    r"\s+[i,I][s,S]\s+[n,N][o,O][t,T]\s+[n,N][u,U][l,L]{2}\s+|\s+[i,I][s,S]\s+[n,N][u,U][l,L]{2}\s+"
)
LOGICAL_OPERATORS_PATTERN = re.compile(
    r"\s+[a,A][n,N][d,D] [n,N][o,O][t,T]\s+|\s+[a,A][n,N][d,D]\s+|"
    r"\s+[o,O][r,R] [n,N][o,O][t,T]\s+|\s+[o,O][r,R]\s+"
)


def sql2pyarrow_filter(string: str, schema: pa.Schema) -> pc.Expression:
    """
    Generates a filter expression for PyArrow based on a given string and schema.

    Parameters:
        string (str): The string containing the filter expression.
        schema (pa.Schema): The PyArrow schema used to validate the filter expression.

    Returns:
        pc.Expression: The generated filter expression.

    Raises:
        ValueError: If the input string is invalid or contains unsupported operations.
    """

    def parse_value(val: str, type_: pa.DataType) -> Any:
        """Parse and convert value based on the field type."""
        if isinstance(val, (tuple, list)):
            return type(val)(parse_value(v, type_) for v in val)

        if pa.types.is_timestamp(type_):
            return timestamp_from_string(val, exact=False, tz=type_.tz)
        elif pa.types.is_date(type_):
            return timestamp_from_string(val, exact=True).date()
        elif pa.types.is_time(type_):
            return timestamp_from_string(val, exact=True).time()

        elif pa.types.is_integer(type_):
            return int(float(val.strip("'").replace(",", ".")))
        elif pa.types.is_floating(type_):
            return float(val.strip("'").replace(",", "."))
        elif pa.types.is_boolean(type_):
            return val.lower().strip("'") in ("true", "1", "yes")
        else:
            return val.strip("'")

    def _parse_part(part: str) -> pc.Expression:
        match = SPLIT_PATTERN.search(part)
        if not match:
            raise ValueError(f"Invalid condition: {part}")

        sign = match.group().lower().strip()
        field, val = [p.strip() for p in SPLIT_PATTERN.split(part)]

        if field not in schema.names:
            raise ValueError(f"Unknown field: {field}")

        type_ = schema.field(field).type
        val = parse_value(val, type_)

        operations = {
            ">=": lambda f, v: pc.field(f) >= v,
            ">": lambda f, v: pc.field(f) > v,
            "<=": lambda f, v: pc.field(f) <= v,
            "<": lambda f, v: pc.field(f) < v,
            "=": lambda f, v: pc.field(f) == v,
            "!=": lambda f, v: pc.field(f) != v,
            "in": lambda f, v: pc.field(f).isin(v),
            "not in": lambda f, v: ~pc.field(f).isin(v),
            "is null": lambda f, v: pc.field(f).is_null(nan_is_null=True),
            "is not null": lambda f, v: ~pc.field(f).is_null(nan_is_null=True),
        }

        if sign not in operations:
            raise ValueError(f"Unsupported operation: {sign}")

        return operations[sign](field, val)

    parts = LOGICAL_OPERATORS_PATTERN.split(string)
    operators = [op.lower().strip() for op in LOGICAL_OPERATORS_PATTERN.findall(string)]

    if len(parts) == 1:
        return _parse_part(parts[0])

    expr = _parse_part(parts[0])
    for part, operator in zip(parts[1:], operators):
        if operator == "and":
            expr = expr & _parse_part(part)
        elif operator == "and not":
            expr = expr & ~_parse_part(part)
        elif operator == "or":
            expr = expr | _parse_part(part)
        elif operator == "or not":
            expr = expr | ~_parse_part(part)
        else:
            raise ValueError(f"Unsupported logical operator: {operator}")

    return expr


def sql2polars_filter(string: str, schema: pl.Schema) -> pl.Expr:
    """
    Generates a filter expression for Polars based on a given string and schema.

    Parameters:
        string (str): The string containing the filter expression.
        schema (pl.Schema): The Polars schema used to validate the filter expression.

    Returns:
        pl.Expr: The generated filter expression.

    Raises:
        ValueError: If the input string is invalid or contains unsupported operations.
    """

    def parse_value(val: str, dtype: pl.DataType) -> Any:
        """Parse and convert value based on the field type."""
        if isinstance(val, (tuple, list)):
            return type(val)(parse_value(v, dtype) for v in val)

        if dtype == pl.Datetime:
            return timestamp_from_string(val, exact=False, tz=dtype.time_zone)
        elif dtype == pl.Date:
            return timestamp_from_string(val, exact=True).date()
        elif dtype == pl.Time:
            return timestamp_from_string(val, exact=True).time()
        elif dtype in (pl.Int8, pl.Int16, pl.Int32, pl.Int64):
            return int(float(val.strip("'").replace(",", ".")))
        elif dtype in (pl.Float32, pl.Float64):
            return float(val.strip("'").replace(",", "."))
        elif dtype == pl.Boolean:
            return val.lower().strip("'") in ("true", "1", "yes")
        else:
            return val.strip("'")

    def _parse_part(part: str) -> pl.Expr:
        match = SPLIT_PATTERN.search(part)
        if not match:
            raise ValueError(f"Invalid condition: {part}")

        sign = match.group().lower().strip()
        field, val = [p.strip() for p in SPLIT_PATTERN.split(part)]

        if field not in schema.names():
            raise ValueError(f"Unknown field: {field}")

        dtype = schema[field]
        val = parse_value(val, dtype)

        operations = {
            ">=": lambda f, v: pl.col(f) >= v,
            ">": lambda f, v: pl.col(f) > v,
            "<=": lambda f, v: pl.col(f) <= v,
            "<": lambda f, v: pl.col(f) < v,
            "=": lambda f, v: pl.col(f) == v,
            "!=": lambda f, v: pl.col(f) != v,
            "in": lambda f, v: pl.col(f).is_in(v),
            "not in": lambda f, v: ~pl.col(f).is_in(v),
            "is null": lambda f, v: pl.col(f).is_null(),
            "is not null": lambda f, v: pl.col(f).is_not_null(),
        }

        if sign not in operations:
            raise ValueError(f"Unsupported operation: {sign}")

        return operations[sign](field, val)

    parts = LOGICAL_OPERATORS_PATTERN.split(string)
    operators = [op.lower().strip() for op in LOGICAL_OPERATORS_PATTERN.findall(string)]

    if len(parts) == 1:
        return _parse_part(parts[0])

    expr = _parse_part(parts[0])
    for part, operator in zip(parts[1:], operators):
        if operator == "and":
            expr = expr & _parse_part(part)
        elif operator == "and not":
            expr = expr & ~_parse_part(part)
        elif operator == "or":
            expr = expr | _parse_part(part)
        elif operator == "or not":
            expr = expr | ~_parse_part(part)
        else:
            raise ValueError(f"Unsupported logical operator: {operator}")

    return expr


def get_table_names(sql_query):
    return [table.name for table in parse_one(sql_query).find_all(exp.Table)]
