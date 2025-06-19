import importlib
import logging
from typing import Any, Callable, Dict, Union

logger = logging.getLogger(__name__)


class CallbackRegistry:
    """
    A registry for managing and retrieving callable functions for RQ job callbacks.
    This helps in serializing callbacks by using string identifiers instead of direct callables.
    """

    _registry: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, func: Callable):
        """Registers a callable function with a unique name."""
        if not callable(func):
            raise ValueError(f"Registered item for '{name}' must be callable.")
        cls._registry[name] = func
        logger.debug(f"Registered callback: {name}")

    @classmethod
    def get(cls, name: str) -> Callable:
        """Retrieves a registered callable function by its name."""
        func = cls._registry.get(name)
        if func is None:
            raise ValueError(f"Callback '{name}' not found in registry.")
        return func

    @classmethod
    def resolve_callback(
        cls, callback_info: Union[str, Callable, None]
    ) -> Union[Callable, None]:
        """
        Resolves a callback from various inputs:
        - If it's a string, tries to get from registry or import it.
        - If it's a callable, returns it directly.
        - If None, returns None.
        """
        if callback_info is None:
            return None
        if callable(callback_info):
            return callback_info
        if isinstance(callback_info, str):
            # Try to get from registry first
            if callback_info in cls._registry:
                return cls._registry[callback_info]
            # Then try to import it as a module path
            try:
                module_path, func_name = callback_info.rsplit(".", 1)
                module = importlib.import_module(module_path)
                func = getattr(module, func_name)
                if callable(func):
                    return func
                else:
                    logger.warning(
                        f"Resolved '{callback_info}' but it is not callable."
                    )
                    return None
            except (ImportError, AttributeError, ValueError) as e:
                logger.error(
                    f"Could not resolve callback string '{callback_info}': {e}"
                )
                return None
        logger.warning(
            f"Invalid callback info type: {type(callback_info)}. Must be str, Callable, or None."
        )
        return None


# Register default callbacks (example)
def default_success_callback(job, connection, result, *args, **kwargs):
    logger.info(f"Job {job.id} completed successfully. Result: {result}")


def default_failure_callback(job, connection, type, value, traceback):
    logger.error(f"Job {job.id} failed. Exception: {type.__name__}: {value}")


CallbackRegistry.register("default_success_callback", default_success_callback)
CallbackRegistry.register("default_failure_callback", default_failure_callback)
