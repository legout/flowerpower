"""Security utilities for input validation and sanitization."""

import re
from pathlib import Path
from typing import Any


class SecurityError(Exception):
    """Raised when security validation fails."""

    pass


def validate_file_path(
    path: str | Path,
    allowed_extensions: list[str] | None = None,
    allow_absolute: bool = True,
    allow_relative: bool = True,
) -> Path:
    """Validate and sanitize file paths to prevent directory traversal attacks.

    Args:
        path: File path to validate
        allowed_extensions: List of allowed file extensions (e.g., ['.yaml', '.yml'])
        allow_absolute: Whether to allow absolute paths
        allow_relative: Whether to allow relative paths

    Returns:
        Validated Path object

    Raises:
        SecurityError: If path is invalid or potentially dangerous
        ValueError: If path is empty or None
    """
    if not path:
        raise ValueError("Path cannot be empty or None")

    # Convert to Path object
    path_obj = Path(path)

    # Check for directory traversal attempts
    path_str = str(path_obj)
    if ".." in path_obj.parts or path_str.startswith(".."):
        raise SecurityError(f"Directory traversal detected in path: {path}")

    # Check absolute vs relative path restrictions
    if path_obj.is_absolute() and not allow_absolute:
        raise SecurityError(f"Absolute paths not allowed: {path}")

    if not path_obj.is_absolute() and not allow_relative:
        raise SecurityError(f"Relative paths not allowed: {path}")

    # Validate file extension if specified
    if allowed_extensions:
        allowed_suffixes = {ext.lower() for ext in allowed_extensions}
        if path_obj.suffix.lower() not in allowed_suffixes:
            raise SecurityError(
                f"File extension '{path_obj.suffix}' not allowed. "
                f"Allowed: {allowed_extensions}"
            )

    # Check for potentially dangerous characters
    dangerous_chars = ["|", "&", ";", "`", "$", "<", ">", '"', "'"]
    if any(char in path_str for char in dangerous_chars):
        raise SecurityError(f"Dangerous characters detected in path: {path}")

    return path_obj


def validate_pipeline_name(name: str) -> str:
    """Validate pipeline name to prevent injection attacks.

    Args:
        name: Pipeline name to validate

    Returns:
        Validated name

    Raises:
        ValueError: If name is invalid
        SecurityError: If name contains dangerous characters
    """
    if not name or not isinstance(name, str):
        raise ValueError("Pipeline name must be a non-empty string")

    name = name.strip()
    if not name:
        raise ValueError("Pipeline name cannot be empty or only whitespace")

    # Check for dangerous characters (dots allowed for dotted pipeline names like group.name)
    if not re.match(r"^[a-zA-Z0-9_.-]+$", name):
        raise SecurityError(
            f"Pipeline name '{name}' contains invalid characters. "
            "Only alphanumeric, underscore, hyphen, and dot are allowed."
        )

    # Reject leading, trailing, or consecutive dots
    if name.startswith(".") or name.endswith(".") or ".." in name:
        raise SecurityError(
            f"Pipeline name '{name}' has invalid dot usage "
            "(leading, trailing, or consecutive dots are not allowed)."
        )

    # Check length constraints
    if len(name) > 100:
        raise SecurityError(f"Pipeline name too long: {len(name)} > 100 characters")

    return name


def validate_directory_fragment(path: str | None) -> str | None:
    """Validate a relative directory fragment used to build config paths.

    Empty strings are preserved so callers can intentionally target the project
    root. Absolute paths and traversal segments are rejected.
    """
    if path is None:
        return None

    if path == "":
        return ""

    validate_file_path(path, allow_absolute=False, allow_relative=True)
    return path


def validate_config_dict(
    config: dict[str, Any],
    allowed_keys: list[str] | None = None,
    max_depth: int = 10,
) -> dict[str, Any]:
    """Validate configuration dictionary to prevent malicious content.

    Args:
        config: Configuration dictionary to validate
        allowed_keys: List of allowed top-level keys
        max_depth: Maximum nesting depth to prevent DoS attacks

    Returns:
        Validated configuration dictionary

    Raises:
        SecurityError: If configuration contains dangerous content
        ValueError: If configuration is invalid
    """
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")

    # Check for allowed keys
    if allowed_keys:
        invalid_keys = set(config.keys()) - set(allowed_keys)
        if invalid_keys:
            raise SecurityError(f"Invalid configuration keys: {invalid_keys}")

    # Check nesting depth
    def check_depth(obj, depth=0):
        if depth > max_depth:
            raise SecurityError(
                f"Configuration nesting too deep: {depth} > {max_depth}"
            )

        if isinstance(obj, dict):
            for value in obj.values():
                check_depth(value, depth + 1)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                check_depth(item, depth + 1)

    check_depth(config)

    return config


def sanitize_log_data(data: Any) -> Any:
    """Sanitize data for safe logging to prevent log injection.

    Args:
        data: Data to sanitize for logging

    Returns:
        Sanitized data safe for logging
    """
    if isinstance(data, str):
        # Remove potential log injection characters
        sanitized = re.sub(r"[\r\n\t]", " ", data)
        # Limit length to prevent log flooding
        if len(sanitized) > 1000:
            sanitized = sanitized[:997] + "..."
        return sanitized
    elif isinstance(data, (dict, list)):
        # For complex objects, convert to string and sanitize
        return sanitize_log_data(str(data))
    else:
        return data


def validate_executor_type(executor_type: str) -> str:
    """Validate executor type to prevent arbitrary code execution.

    Args:
        executor_type: Executor type string to validate

    Returns:
        Validated executor type

    Raises:
        SecurityError: If executor type is invalid or dangerous
    """
    if not executor_type or not isinstance(executor_type, str):
        raise ValueError("Executor type must be a non-empty string")

    allowed_executors = {
        "synchronous",
        "local",
        "threadpool",
        "processpool",
        "ray",
        "dask",
    }

    if executor_type not in allowed_executors:
        raise SecurityError(
            f"Invalid executor type: {executor_type}. "
            f"Allowed types: {allowed_executors}"
        )

    return executor_type


def validate_callback_function(callback: Any) -> bool:
    """Validate callback function to ensure it's safe to execute.

    Args:
        callback: Callback function or callable to validate

    Returns:
        True if callback is valid

    Raises:
        SecurityError: If callback is dangerous or invalid
    """
    if callback is None:
        return True

    if not callable(callback):
        raise SecurityError("Callback must be callable")

    # Check if it's a built-in function that could be dangerous
    dangerous_functions = {"eval", "exec", "compile", "__import__"}
    if hasattr(callback, "__name__") and callback.__name__ in dangerous_functions:
        raise SecurityError(f"Dangerous callback function: {callback.__name__}")

    return True
