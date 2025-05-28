import functools
import inspect
from typing import Any, Callable, Dict, Tuple

from loguru import logger

from ..settings import LOG_LEVEL
from .logging import setup_logging

# Configure a logger. In a real application, you might get this from a central logging config.
# To see the debug logs from the decorator, set the logging level:
# logging.basicConfig(level=logging.DEBUG)

setup_logging(level=LOG_LEVEL)


def _execute_callback(callback_info: Any, context_exception: Exception = None):
    """
    Helper to execute a callback.
    The callback_info can be a callable, or a tuple (callable, args_tuple, kwargs_dict).
    If context_exception is provided (for on_failure), it can be passed to the callback.
    """
    if not callback_info:
        return

    callback_fn: Callable = None
    cb_args: Tuple = ()
    cb_kwargs: Dict[str, Any] = {}

    is_simple_callable = isinstance(callback_info, Callable)

    if is_simple_callable:
        callback_fn = callback_info
        # For a simple callable in an on_failure context, try to pass the exception.
        if context_exception:
            try:
                sig = inspect.signature(callback_fn)
                if len(sig.parameters) == 1:  # Assumes it takes one positional argument
                    first_param_name = list(sig.parameters.keys())[0]
                    # Avoid passing if it's a **kwargs style param and we have no other indication
                    if sig.parameters[first_param_name].kind in [
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        inspect.Parameter.POSITIONAL_ONLY,
                    ]:
                        cb_args = (context_exception,)
                elif (
                    "exception" in sig.parameters
                ):  # Or if it explicitly takes 'exception' kwarg
                    cb_kwargs["exception"] = context_exception
            except (ValueError, TypeError):  # Some callables might not be inspectable
                logger.debug(
                    f"Could not inspect signature for simple callback {getattr(callback_fn, '__name__', str(callback_fn))}. Exception not passed automatically."
                )

    elif (
        isinstance(callback_info, tuple)
        and len(callback_info) > 0
        and isinstance(callback_info[0], Callable)
    ):
        callback_fn = callback_info[0]

        # Args: callback_info[1]
        if len(callback_info) > 1 and callback_info[1] is not None:
            if isinstance(callback_info[1], tuple):
                cb_args = callback_info[1]
            else:
                logger.warning(
                    f"Callback args for {getattr(callback_fn, '__name__', str(callback_fn))} "
                    f"expected tuple, got {type(callback_info[1])}. Ignoring args."
                )

        # Kwargs: callback_info[2]
        if len(callback_info) > 2 and callback_info[2] is not None:
            if isinstance(callback_info[2], dict):
                cb_kwargs = callback_info[2].copy()  # Use a copy
            else:
                logger.warning(
                    f"Callback kwargs for {getattr(callback_fn, '__name__', str(callback_fn))} "
                    f"expected dict, got {type(callback_info[2])}. Ignoring kwargs."
                )

        # If this is an on_failure call and an exception occurred,
        # pass it if 'exception' kwarg is not set and the callback accepts it.
        if context_exception and "exception" not in cb_kwargs:
            try:
                sig = inspect.signature(callback_fn)
                if "exception" in sig.parameters:
                    cb_kwargs["exception"] = context_exception
            except (ValueError, TypeError):  # Some callables might not be inspectable
                pass  # Cannot inspect, so don't add

    if callback_fn:
        try:
            callback_name = getattr(callback_fn, "__name__", str(callback_fn))
            logger.debug(f"Executing callback: {callback_name}")
            callback_fn(*cb_args, **cb_kwargs)
        except Exception as cb_e:
            callback_name_err = getattr(callback_fn, "__name__", str(callback_fn))
            logger.error(
                f"Error executing callback {callback_name_err}: {cb_e}", exc_info=True
            )
    else:
        logger.warning(
            f"Invalid callback_info format or non-callable provided: {callback_info}"
        )


def run_with_callback(on_success: Any = None, on_failure: Any = None):
    """
    A Python decorator that executes a function within a try-except-finally block,
    allowing for `on_success` and `on_failure` callbacks.

    The `on_success` and `on_failure` arguments can be:
    1. A callable: `my_callback_func`
       - If `on_failure` is a simple callable that accepts one argument or an
         `exception` keyword argument, the caught exception will be passed.
    2. A tuple: `(my_callback_func, (arg1, arg2), {"kwarg1": val1})`
       - The args tuple and kwargs dict are optional (can be `None` or empty).
       - If `on_failure` is used and an exception occurs, the exception instance
         will be passed as a keyword argument `exception` to the failure callback,
         provided the callback accepts it and it's not already in the user-supplied kwargs.

    The decorated function's return value is returned if successful.
    If an exception occurs in the decorated function, it is re-raised after
    the `on_failure` callback is attempted.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            success_flag = False
            result_value = None
            caught_exception = None
            try:
                result_value = func(*args, **kwargs)
                success_flag = True
                return result_value
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {e}", exc_info=True)
                success_flag = False
                caught_exception = e
                # The original exception will be re-raised after the finally block.
                raise
            finally:
                if success_flag:
                    if on_success:
                        # logger.debug(f"Executing on_success callback for {func.__name__}")
                        _execute_callback(on_success)
                else:
                    if on_failure:
                        # logger.debug(f"Executing on_failure callback for {func.__name__}")
                        _execute_callback(
                            on_failure, context_exception=caught_exception
                        )

        return wrapper

    return decorator
