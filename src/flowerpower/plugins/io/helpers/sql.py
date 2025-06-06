import re
from typing import Any

import pyarrow as pa
import pyarrow.compute as pc
from sqlglot import exp, parse_one

from .datetime import timestamp_from_string
from .polars import pl

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
