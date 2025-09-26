import warnings
import msgspec
import importlib
from munch import munchify
from typing import Any, Callable
from requests.exceptions import HTTPError, ConnectionError, Timeout # Example exception
from ... import settings
from ..base import BaseConfig


class WithAdapterConfig(BaseConfig):
    hamilton_tracker: bool = msgspec.field(default=False)
    mlflow: bool = msgspec.field(default=False)
    # openlineage: bool = msgspec.field(default=False)
    ray: bool = msgspec.field(default=False)
    opentelemetry: bool = msgspec.field(default=False)
    progressbar: bool = msgspec.field(default=False)
    future: bool = msgspec.field(default=False)


class ExecutorConfig(BaseConfig):
    type: str | None = msgspec.field(default=settings.EXECUTOR)
    max_workers: int | None = msgspec.field(default=settings.EXECUTOR_MAX_WORKERS)
    num_cpus: int | None = msgspec.field(default=settings.EXECUTOR_NUM_CPUS)


class CallbackSpec(msgspec.Struct):
    """Specification for a callback function with optional arguments."""
    func: Callable
    args: tuple | None = None
    kwargs: dict | None = None


class RunConfig(BaseConfig):
    inputs: dict | None = msgspec.field(default_factory=dict)
    final_vars: list[str] | None = msgspec.field(default_factory=list)
    config: dict | None = msgspec.field(default_factory=dict)
    cache: dict | bool | None = msgspec.field(default=False)
    with_adapter: WithAdapterConfig = msgspec.field(default_factory=WithAdapterConfig)
    executor: ExecutorConfig = msgspec.field(default_factory=ExecutorConfig)
    log_level: str | None = msgspec.field(default="INFO")
    max_retries: int = msgspec.field(default=3)
    retry_delay: int | float = msgspec.field(default=1)
    jitter_factor: float | None = msgspec.field(default=0.1)
    retry_exceptions: list[str] = msgspec.field(default_factory=lambda: ["Exception"])
    # New fields for comprehensive configuration
    pipeline_adapter_cfg: dict | None = msgspec.field(default=None)
    project_adapter_cfg: dict | None = msgspec.field(default=None)
    adapter: dict[str, Any] | None = msgspec.field(default=None)
    reload: bool = msgspec.field(default=False)
    on_success: CallbackSpec | None = msgspec.field(default=None)
    on_failure: CallbackSpec | None = msgspec.field(default=None)

    def __post_init__(self):
        # if isinstance(self.inputs, dict):
        #     self.inputs = munchify(self.inputs)
        if isinstance(self.config, dict):
            self.config = munchify(self.config)
        if isinstance(self.cache, (dict)):
            self.cache = munchify(self.cache)
        if isinstance(self.with_adapter, dict):
            self.with_adapter = WithAdapterConfig.from_dict(self.with_adapter)
        if isinstance(self.executor, dict):
            self.executor = ExecutorConfig.from_dict(self.executor)
        if isinstance(self.pipeline_adapter_cfg, dict):
            from ..pipeline.adapter import AdapterConfig as PipelineAdapterConfig
            self.pipeline_adapter_cfg = PipelineAdapterConfig.from_dict(self.pipeline_adapter_cfg)
        if isinstance(self.project_adapter_cfg, dict):
            from ..project.adapter import AdapterConfig as ProjectAdapterConfig
            self.project_adapter_cfg = ProjectAdapterConfig.from_dict(self.project_adapter_cfg)
        if isinstance(self.adapter, dict):
            # Convert adapter instances if needed
            pass
        if isinstance(self.retry_exceptions, list):
            # Convert string exceptions to actual exception classes using dynamic import
            self.retry_exceptions = self._convert_exception_strings(self.retry_exceptions)

        # Handle callback conversions
        if self.on_success is not None and not isinstance(self.on_success, CallbackSpec):
            if callable(self.on_success):
                self.on_success = CallbackSpec(func=self.on_success)
            elif isinstance(self.on_success, tuple) and len(self.on_success) == 3:
                func, args, kwargs = self.on_success
                self.on_success = CallbackSpec(func=func, args=args, kwargs=kwargs)
            else:
                self.on_success = None
                warnings.warn(
                    "Invalid on_success format, must be Callable or (Callable, args, kwargs)",
                    RuntimeWarning
                )
    
    def _convert_exception_strings(self, exception_list: list) -> list:
        """Convert exception strings to actual exception classes using dynamic import.
        
        Args:
            exception_list: List of exception names or classes.
            
        Returns:
            List of exception classes.
        """
        converted_exceptions = []
        
        for exc in exception_list:
            if isinstance(exc, str):
                try:
                    # Try to dynamically import the exception class
                    exc_class = self._import_exception_class(exc)
                    converted_exceptions.append(exc_class)
                except (ImportError, AttributeError) as e:
                    warnings.warn(
                        f"Could not import exception class '{exc}': {e}. Using Exception instead.",
                        RuntimeWarning
                    )
                    converted_exceptions.append(Exception)
            elif isinstance(exc, type) and issubclass(exc, BaseException):
                converted_exceptions.append(exc)
            else:
                warnings.warn(
                    f"Invalid exception type: {type(exc)}. Using Exception instead.",
                    RuntimeWarning
                )
                converted_exceptions.append(Exception)
        
        return converted_exceptions
    
    def _import_exception_class(self, exception_name: str) -> type:
        """Dynamically import an exception class by name.
        
        Args:
            exception_name: Name of the exception class to import.
            
        Returns:
            The imported exception class.
            
        Raises:
            ImportError: If the module cannot be imported.
            AttributeError: If the exception class is not found in the module.
        """
        # Handle built-in exceptions first
        built_in_exceptions = {
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'RuntimeError': RuntimeError,
            'FileNotFoundError': FileNotFoundError,
            'PermissionError': PermissionError,
            'KeyError': KeyError,
            'AttributeError': AttributeError,
            'ImportError': ImportError,
            'TimeoutError': TimeoutError,
        }
        
        if exception_name in built_in_exceptions:
            return built_in_exceptions[exception_name]
        
        # Handle module-qualified exceptions (e.g., 'requests.exceptions.HTTPError')
        if '.' in exception_name:
            module_name, class_name = exception_name.rsplit('.', 1)
            module = importlib.import_module(module_name)
            return getattr(module, class_name)
        
        # Try to import from common modules
        common_modules = [
            'requests.exceptions',
            'urllib.error',
            'urllib3.exceptions',
            'http.client',
            'socket',
            'os',
            'io',
        ]
        
        for module_name in common_modules:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, exception_name):
                    return getattr(module, exception_name)
            except ImportError:
                continue
        
        # If not found in common modules, raise an error
        raise ImportError(f"Could not find exception class: {exception_name}")

        if self.on_failure is not None and not isinstance(self.on_failure, CallbackSpec):
            if callable(self.on_failure):
                self.on_failure = CallbackSpec(func=self.on_failure)
            elif isinstance(self.on_failure, tuple) and len(self.on_failure) == 3:
                func, args, kwargs = self.on_failure
                self.on_failure = CallbackSpec(func=func, args=args, kwargs=kwargs)
            else:
                self.on_failure = None
                warnings.warn(
                    "Invalid on_failure format, must be Callable or (Callable, args, kwargs)",
                    RuntimeWarning
                )
