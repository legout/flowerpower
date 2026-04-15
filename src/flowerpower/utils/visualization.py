"""Visualization utilities for image viewing and display.

This module contains UI-oriented helpers for displaying images using
the system's default image viewer. Used primarily by pipeline visualization.
"""

import os
import subprocess
import tempfile
import time

from .security import validate_file_path


def _validate_image_format(format: str) -> str:
    """Validate image format to prevent injection attacks.

    Args:
        format: Image format to validate

    Returns:
        str: Validated format

    Raises:
        ValueError: If format is not supported
    """
    allowed_formats = {"svg", "png", "jpg", "jpeg", "gif", "pdf", "html"}
    if format not in allowed_formats:
        raise ValueError(f"Unsupported format: {format}. Allowed: {allowed_formats}")
    return format


def _create_temp_image_file(data: str | bytes, format: str) -> str:
    """Create a temporary file with image data.

    Args:
        data: Image data as string or bytes
        format: Validated image format

    Returns:
        str: Path to temporary file

    Raises:
        OSError: If file creation fails
    """
    with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp:
        if isinstance(data, str):
            tmp.write(data.encode("utf-8"))
        else:
            tmp.write(data)
        tmp_path = tmp.name

    # Validate the temporary file path for security
    validate_file_path(tmp_path, allow_relative=False)
    return tmp_path


def _open_image_viewer(tmp_path: str) -> None:
    """Open image viewer with the given file path.

    Args:
        tmp_path: Path to temporary image file

    Raises:
        OSError: If platform is not supported
        subprocess.CalledProcessError: If subprocess fails
        subprocess.TimeoutExpired: If subprocess times out
    """
    import platform

    platform_system = platform.system()

    if platform_system == "Darwin":  # macOS
        subprocess.run(["open", tmp_path], check=True, timeout=10)
    elif platform_system == "Linux":
        subprocess.run(["xdg-open", tmp_path], check=True, timeout=10)
    elif platform_system == "Windows":
        startfile = getattr(os, "startfile", None)
        if startfile is None:
            raise OSError("os.startfile is unavailable on this platform")
        startfile(tmp_path)
    else:
        raise OSError(f"Unsupported platform: {platform_system}")


def _cleanup_temp_file(tmp_path: str) -> None:
    """Clean up temporary file.

    Args:
        tmp_path: Path to temporary file to remove
    """
    try:
        os.unlink(tmp_path)
    except OSError:
        pass  # File might already be deleted or in use


def view_img(data: str | bytes, format: str = "svg"):
    """View image data using the system's default image viewer.

    Args:
        data: Image data as string or bytes
        format: Image format (svg, png, jpg, jpeg, gif, pdf, html)

    Raises:
        ValueError: If format is not supported
        RuntimeError: If file opening fails
        OSError: If platform is not supported
    """
    # Validate format to prevent injection attacks
    validated_format = _validate_image_format(format)

    # Create a temporary file with validated extension
    tmp_path = _create_temp_image_file(data, validated_format)

    try:
        # Open image viewer with secure subprocess call
        _open_image_viewer(tmp_path)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as e:
        # Clean up temp file on error
        _cleanup_temp_file(tmp_path)
        raise RuntimeError(f"Failed to open file: {e}") from e

    # Optional: Remove the temp file after a delay
    time.sleep(2)  # Wait for viewer to open
    _cleanup_temp_file(tmp_path)
