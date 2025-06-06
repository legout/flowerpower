import datetime as dt
import re
from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# import pendulum as pdl
import polars as pl
import polars.selectors as cs
import pyarrow as pa


def get_timestamp_column(df: pl.DataFrame | pl.LazyFrame | pa.Table) -> str | list[str]:
    if isinstance(df, pa.Table):
        df = pl.from_arrow(df).lazy()

    # if isinstance(df, pl.LazyFrame):
    #    return df.collect_schema().names()

    return df.select(cs.datetime() | cs.date()).collect_schema().names()


def get_timedelta_str(timedelta_string: str, to: str = "polars") -> str:
    polars_timedelta_units = [
        "ns",
        "us",
        "ms",
        "s",
        "m",
        "h",
        "d",
        "w",
        "mo",
        "y",
    ]
    duckdb_timedelta_units = [
        "nanosecond",
        "microsecond",
        "millisecond",
        "second",
        "minute",
        "hour",
        "day",
        "week",
        "month",
        "year",
    ]

    unit = re.sub("[0-9]", "", timedelta_string).strip()
    val = timedelta_string.replace(unit, "").strip()
    if to == "polars":
        return (
            timedelta_string
            if unit in polars_timedelta_units
            else val
            + dict(zip(duckdb_timedelta_units, polars_timedelta_units))[
                re.sub("s$", "", unit)
            ]
        )

    if unit in polars_timedelta_units:
        return (
            f"{val} " + dict(zip(polars_timedelta_units, duckdb_timedelta_units))[unit]
        )

    return f"{val} " + re.sub("s$", "", unit)


# @lru_cache(maxsize=128)
# def timestamp_from_string(
#     timestamp: str,
#     tz: str | None = None,
#     exact: bool = True,
#     strict: bool = False,
#     naive: bool = False,
# ) -> pdl.DateTime | pdl.Date | pdl.Time | dt.datetime | dt.date | dt.time:
#     """
#     Converts a string like "2023-01-01 10:00:00" into a datetime.datetime object.

#     Args:
#         string (str): The string representation of the timestamp, e.g. "2023-01-01 10:00:00".
#         tz (str, optional): The timezone to use for the timestamp. Defaults to None.
#         exact (bool, optional): Whether to use exact parsing. Defaults to True.
#         strict (bool, optional): Whether to use strict parsing. Defaults to False.
#         naive (bool, optional): Whether to return a naive datetime without a timezone. Defaults to False.

#     Returns:
#         datetime.datetime: The datetime object.
#     """
#     # Extract the timezone from the string if not provided
#     # tz = extract_timezone(timestamp) if tz is None else tz
#     # timestamp = timestamp.replace(tz, "").strip() if tz else timestamp

#     pdl_timestamp = pdl.parse(timestamp, exact=exact, strict=strict)

#     if isinstance(pdl_timestamp, pdl.DateTime):
#         if tz is not None:
#             pdl_timestamp = pdl_timestamp.naive().set(tz=tz)
#         if naive or tz is None:
#             pdl_timestamp = pdl_timestamp.naive()

#     return pdl_timestamp


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


# def timedelta_from_string(
#     timedelta_string: str, as_timedelta
# ) -> pdl.Duration | dt.timedelta:
#     """
#     Converts a string like "2d10s" into a datetime.timedelta object.

#     Args:
#         string (str): The string representation of the timedelta, e.g. "2d10s".

#     Returns:
#         datetime.timedelta: The timedelta object.
#     """
#     # Extract the numeric value and the unit from the string
#     matches = re.findall(r"(\d+)([a-zA-Z]+)", timedelta_string)
#     if not matches:
#         raise ValueError("Invalid timedelta string")

#     # Initialize the timedelta object
#     delta = pdl.duration()

#     # Iterate over each match and accumulate the timedelta values
#     for value, unit in matches:
#         # Map the unit to the corresponding timedelta attribute
#         unit_mapping = {
#             "us": "microseconds",
#             "ms": "milliseconds",
#             "s": "seconds",
#             "m": "minutes",
#             "h": "hours",
#             "d": "days",
#             "w": "weeks",
#             "mo": "months",
#             "y": "years",
#         }
#         if unit not in unit_mapping:
#             raise ValueError("Invalid timedelta unit")

#         # Update the timedelta object
#         kwargs = {unit_mapping[unit]: int(value)}
#         delta += pdl.duration(**kwargs)

#     return delta.as_timedelta if as_timedelta else delta


# def extract_timezone(timestamp_string):
#     """
#     Extracts the timezone from a timestamp string.

#     Args:
#         timestamp_string (str): The input timestamp string.

#     Returns:
#         str: The extracted timezone.
#     """
#     pattern = r"\b([a-zA-Z]+/{0,1}[a-zA-Z_ ]*)\b"  # Matches the timezone portion
#     match = re.search(pattern, timestamp_string)
#     if match:
#         timezone = match.group(0)
#         return timezone
#     else:
#         return None
