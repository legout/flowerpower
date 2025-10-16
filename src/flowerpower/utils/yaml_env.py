"""
YAML environment variable interpolation utilities.

Supports a Docker Compose–style syntax inside YAML values:
- ${VAR}                -> substitute value of VAR (empty string if unset)
- ${VAR:-default}       -> default if VAR is unset or empty
- ${VAR-default}        -> default if VAR is unset (but not when set to empty)
- ${VAR:?err}           -> raise error if VAR is unset or empty
- ${VAR?err}            -> raise error if VAR is unset (but not when set to empty)
- $VAR                  -> simple substitution for alnum/underscore names
- $$                    -> escaped dollar sign

After interpolation, if the resulting string is valid JSON (object/array/number/bool/null),
it is coerced to the corresponding Python type. Otherwise the string is returned.

This module performs interpolation after YAML is parsed, by recursively walking the
loaded dict/list structure and transforming string values in-place.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Mapping


_VAR_PATTERN = re.compile(
    r"\$\$|\$\{[^}]+\}|\$[A-Za-z_][A-Za-z0-9_]*"
)


def _is_empty(value: str | None) -> bool:
    return value is None or value == ""


def _expand_match(match: re.Match, env: Mapping[str, str]) -> str:
    token = match.group(0)
    # Escaped dollar
    if token == "$$":
        return "\x00_DOLLAR_\x00"  # temporary placeholder

    # ${...} forms
    if token.startswith("${"):
        inner = token[2:-1]
        # Parse operators: :-, -, :?, ?
        op = None
        name = inner
        arg = None
        for candidate in (":-", "-", ":?", "?"):
            if candidate in inner:
                parts = inner.split(candidate, 1)
                name = parts[0]
                op = candidate
                arg = parts[1]
                break

        name = name.strip()
        value = env.get(name)

        if op is None:
            # No operator, empty becomes empty string
            return value if value is not None else ""

        if op == ":-":
            # default if unset or empty
            return value if not _is_empty(value) else (arg or "")
        if op == "-":
            # default if unset only
            return value if value is not None else (arg or "")
        if op == ":?":
            if _is_empty(value):
                raise ValueError(arg or f"Environment variable '{name}' is required")
            return value
        if op == "?":
            if value is None:
                raise ValueError(arg or f"Environment variable '{name}' is required")
            return value

        # Fallback shouldn't occur, but return empty to be safe
        return ""

    # $VAR simple form
    var_name = token[1:]
    return env.get(var_name, "")


def _maybe_json(value: str) -> Any:
    s = value.strip()
    # Fast-path: looks like JSON or a JSON scalar
    if not s:
        return value
    if s[0] in "[{" or s in ("true", "false", "null"):
        try:
            return json.loads(s)
        except Exception:
            return value
    # Try number parsing via json for consistency (handles -1, 1.0)
    if re.fullmatch(r"-?\d+(\.\d+)?", s):
        try:
            return json.loads(s)
        except Exception:
            return value
    return value


def interpolate_string(s: str, env: Mapping[str, str] | None = None, json_coerce: bool = True) -> Any:
    """Interpolate variables in a single string.

    Returns a possibly type-coerced value when json_coerce is True.
    """
    env = env or os.environ
    if "$" not in s:
        return s
    expanded = _VAR_PATTERN.sub(lambda m: _expand_match(m, env), s)
    # Restore escaped dollars
    expanded = expanded.replace("\x00_DOLLAR_\x00", "$")
    return _maybe_json(expanded) if json_coerce else expanded


def interpolate_env_in_data(data: Any, env: Mapping[str, str] | None = None, json_coerce: bool = True) -> Any:
    """Recursively interpolate environment variables for all string values in data.

    Modifies lists and dicts recursively; returns the transformed structure.
    """
    env = env or os.environ

    if isinstance(data, dict):
        return {k: interpolate_env_in_data(v, env=env, json_coerce=json_coerce) for k, v in data.items()}
    if isinstance(data, list):
        return [interpolate_env_in_data(v, env=env, json_coerce=json_coerce) for v in data]
    if isinstance(data, str):
        return interpolate_string(data, env=env, json_coerce=json_coerce)
    return data
