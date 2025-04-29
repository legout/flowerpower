import ast
import importlib
import json
import posixpath
import re
import sys
from pathlib import Path
from typing import Callable

from loguru import logger

from flowerpower.pipeline import PipelineManager

from ..utils.logging import setup_logging

setup_logging()


# Parse additional parameters
def parse_param_dict(param_str: str | None) -> dict:
    """Helper to parse parameter dictionaries"""
    if not param_str:
        return {}
    return dict(param.split("=") for param in param_str.split(","))


def parse_dict_or_list_param(
    value: str | None = None, param_type: str = "dict"
) -> list | dict | None:
    """
    Parse dictionary or list parameters from various input formats.

    Supports:
    - JSON string
    - Python literal (dict/list)
    - Comma-separated key=value pairs (for dicts)
    - Comma-separated values (for lists)
    - List-like string with or without quotes

    Args:
        value (str, optional): Input string to parse
        param_type (str): Type of parameter to parse ('dict' or 'list')

    Returns:
        dict | list | None: Parsed parameter or None if parsing fails
    """

    def convert_string_booleans(obj):
        if isinstance(obj, dict):
            return {k: convert_string_booleans(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_string_booleans(item) for item in obj]
        elif isinstance(obj, str):
            if obj.lower() == "true":
                return True
            elif obj.lower() == "false":
                return False
        return obj

    if value is None:
        return None

    try:
        # Try parsing as JSON first
        parsed = json.loads(value)
        return convert_string_booleans(parsed)
    except json.JSONDecodeError:
        try:
            # Try parsing as Python literal
            parsed = ast.literal_eval(value)

            # Validate type
            if param_type == "dict" and not isinstance(parsed, dict):
                raise ValueError(f"Expected dict, got {type(parsed)}")
            elif param_type == "list" and not isinstance(parsed, list):
                raise ValueError(f"Expected list, got {type(parsed)}")

            return convert_string_booleans(parsed)
        except (SyntaxError, ValueError):
            # For dicts, try parsing as comma-separated key=value pairs
            if param_type == "dict" and "=" in value:
                parsed = dict(
                    pair.split("=", 1) for pair in value.split(",") if pair.strip()
                )
                return convert_string_booleans(parsed)

            # For lists, try multiple parsing strategies
            if param_type == "list":
                # Remove surrounding square brackets and whitespace
                value = value.strip()
                if value.startswith("[") and value.endswith("]"):
                    value = value[1:-1].strip()

                # Parse list-like string with or without quotes
                # This regex handles: a,b | 'a','b' | "a","b" | a, b | 'a', 'b'
                list_items = re.findall(r"['\"]?(.*?)['\"]?(?=\s*,|\s*$)", value)

                # Remove any empty strings and strip whitespace
                parsed = [item.strip() for item in list_items if item.strip()]

                return convert_string_booleans(parsed)

            # If all parsing fails, log warning and return None
            logger.warning(f"Could not parse {param_type} parameter: {value}")
            return None


def load_hook(
    pipeline_name: str,
    function_path: str,
    base_dir=None,
    storage_options: str | None = None,
) -> Callable:
    """
    Load a hook function from a specified path.
    This function dynamically imports the module and retrieves the function


    Args:
        pipeline_name (str): Name of the pipeline
        function_path (str): Path to the function in the format 'module_name.function_name'
        base_dir (str, optional): Base directory for the pipeline
        storage_options (str, optional): Storage options as JSON or dict string
    Returns:
        Callable: The loaded hook function
    """
    with PipelineManager(storage_options=storage_options, base_dir=base_dir) as pm:
        path_segments = function_path.rsplit(".", 2)
        if len(path_segments) == 2:
            # If the function path is in the format 'module_name.function_name'
            module_name, function_name = path_segments
            module_path = ""
        elif len(path_segments) == 3:
            # If the function path is in the format 'package.[subpackage.]module_name.function_name'
            module_path, module_name, function_name = path_segments

        logger.debug(
            posixpath.join(
                pm._fs.path, "hooks", pipeline_name, module_path.replace(".", "/")
            )
        )
        sys.path.append(
            posixpath.join(
                pm._fs.path, "hooks", pipeline_name, module_path.replace(".", "/")
            )
        )
        hook_module = importlib.import_module(module_name)
        hook_function = getattr(hook_module, function_name)
        return hook_function
