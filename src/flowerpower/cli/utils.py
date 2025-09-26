import ast
import importlib
import importlib.util
import json
import os
import posixpath
import re
from typing import Callable

from loguru import logger

from flowerpower.pipeline import PipelineManager

from ..utils.logging import setup_logging

setup_logging()


def convert_string_booleans(obj):
    """Convert string 'true'/'false' to boolean values recursively."""
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


def _parse_json(value: str):
    """Parse value as JSON string."""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def _parse_python_literal(value: str, param_type: str):
    """Parse value as Python literal (dict/list)."""
    try:
        parsed = ast.literal_eval(value)
        
        # Validate type
        if param_type == "dict" and not isinstance(parsed, dict):
            raise ValueError(f"Expected dict, got {type(parsed)}")
        elif param_type == "list" and not isinstance(parsed, list):
            raise ValueError(f"Expected list, got {type(parsed)}")
        
        return parsed
    except (SyntaxError, ValueError):
        return None


def _parse_key_value_pairs(value: str):
    """Parse value as comma-separated key=value pairs."""
    if "=" not in value:
        return None
    
    try:
        return dict(
            pair.split("=", 1) for pair in value.split(",") if pair.strip()
        )
    except ValueError:
        return None


def _parse_comma_separated_list(value: str):
    """Parse value as comma-separated list with optional quotes."""
    # Remove surrounding square brackets and whitespace
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1].strip()
    
    # Parse list-like string with or without quotes
    # This regex handles: a,b | 'a','b' | "a","b" | a, b | 'a', 'b'
    list_items = re.findall(r"['\"]?(.*?)['\"]?(?=\s*,|\s*$)", value)
    
    # Remove any empty strings and strip whitespace
    return [item.strip() for item in list_items if item.strip()]


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
    if value is None:
        return None

    # Try parsing as JSON first
    parsed = _parse_json(value)
    if parsed is not None:
        return convert_string_booleans(parsed)
    
    # Try parsing as Python literal
    parsed = _parse_python_literal(value, param_type)
    if parsed is not None:
        return convert_string_booleans(parsed)
    
    # For dicts, try parsing as comma-separated key=value pairs
    if param_type == "dict":
        parsed = _parse_key_value_pairs(value)
        if parsed is not None:
            return convert_string_booleans(parsed)
    
    # For lists, try parsing as comma-separated values
    if param_type == "list":
        parsed = _parse_comma_separated_list(value)
        if parsed:
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
        else:
            raise ValueError(
                f"Invalid function_path format: {function_path}. "
                "Expected 'module_name.function_name' or 'package.module_name.function_name'"
            )

        # Construct the full path to the module file
        hooks_dir = posixpath.join(
            pm._fs.path, "hooks", pipeline_name, module_path.replace(".", "/")
        )
        module_file_path = os.path.join(hooks_dir, f"{module_name}.py")
        
        logger.debug(f"Loading hook module from: {module_file_path}")
        
        # Validate that the module file exists
        if not os.path.exists(module_file_path):
            raise FileNotFoundError(f"Hook module not found: {module_file_path}")
        
        # Use importlib.util to safely load the module without modifying sys.path
        spec = importlib.util.spec_from_file_location(module_name, module_file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module spec for {module_name} from {module_file_path}")
        
        hook_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hook_module)
        
        # Get the function from the loaded module
        if not hasattr(hook_module, function_name):
            raise AttributeError(f"Function {function_name} not found in module {module_name}")
        
        hook_function = getattr(hook_module, function_name)
        if not callable(hook_function):
            raise TypeError(f"{function_name} is not callable in module {module_name}")
        
        return hook_function
