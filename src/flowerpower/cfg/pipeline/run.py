import warnings
import msgspec
import importlib
from munch import munchify
from typing import Any
from collections.abc import Callable
from requests.exceptions import HTTPError, ConnectionError, Timeout  # Example exception
from ... import settings
from ..base import BaseConfig


DEPRECATED_RETRY_FIELDS = (
    "max_retries",
    "retry_delay",
    "jitter_factor",
    "retry_exceptions",
)

_LEGACY_RETRY_DEFAULTS: dict[str, Any] = {
    "max_retries": 3,
    "retry_delay": 1,
    "jitter_factor": 0.1,
    "retry_exceptions": ["Exception"],
}


def migrate_legacy_retry_fields(run_data: dict[str, Any]) -> bool:
    """Normalize legacy retry fields into nested retry configuration.

    Args:
        run_data: Raw run configuration dictionary loaded from YAML.

    Returns:
        True if the dictionary was mutated, otherwise False.
    """
    if not isinstance(run_data, dict):
        return False

    mutated = False
    existing_retry = run_data.get("retry")
    retry_block = existing_retry if isinstance(existing_retry, dict) else None
    collected: dict[str, Any] = {}

    for field in DEPRECATED_RETRY_FIELDS:
        if field in run_data:
            value = run_data.pop(field)
            mutated = True

            if field == "max_retries" and value is not None:
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    pass
            elif field in {"retry_delay", "jitter_factor"} and value is not None:
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    pass
            elif (
                field == "retry_exceptions"
                and value is not None
                and not isinstance(value, list)
            ):
                value = [value]

            if field == "retry_exceptions":
                if value not in (None, []):
                    collected[field] = value
            elif value is not None:
                collected[field] = value

    if collected:
        if retry_block is None:
            run_data["retry"] = collected
        else:
            merged = retry_block.copy()
            for key, value in collected.items():
                merged.setdefault(key, value)
            run_data["retry"] = merged
        mutated = True

    return mutated


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


class RetryConfig(BaseConfig):
    """Retry configuration for pipeline execution."""

    max_retries: int = msgspec.field(default=3)
    retry_delay: float = msgspec.field(default=1.0)
    jitter_factor: float | None = msgspec.field(default=0.1)
    # Accept strings or classes; will be converted to exception classes in __post_init__
    retry_exceptions: list[Any] = msgspec.field(default_factory=lambda: ["Exception"])  # type: ignore[assignment]

    def __post_init__(self):
        if isinstance(self.retry_exceptions, list):
            self.retry_exceptions = self._convert_exception_strings(
                self.retry_exceptions
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
                    exc_class = self._import_exception_class(exc)
                    converted_exceptions.append(exc_class)
                except (ImportError, AttributeError) as e:
                    warnings.warn(
                        f"Could not import exception class '{exc}': {e}. Using Exception instead.",
                        RuntimeWarning,
                    )
                    converted_exceptions.append(Exception)
            elif isinstance(exc, type) and issubclass(exc, BaseException):
                converted_exceptions.append(exc)
            else:
                warnings.warn(
                    f"Invalid exception type: {type(exc)}. Using Exception instead.",
                    RuntimeWarning,
                )
                converted_exceptions.append(Exception)
        return converted_exceptions

    def _import_exception_class(self, exception_name: str) -> type:
        """Dynamically import an exception class by name."""
        built_in_exceptions = {
            "Exception": Exception,
            "ValueError": ValueError,
            "TypeError": TypeError,
            "RuntimeError": RuntimeError,
            "FileNotFoundError": FileNotFoundError,
            "PermissionError": PermissionError,
            "KeyError": KeyError,
            "AttributeError": AttributeError,
            "ImportError": ImportError,
            "TimeoutError": TimeoutError,
        }
        if exception_name in built_in_exceptions:
            return built_in_exceptions[exception_name]

        if "." in exception_name:
            module_name, class_name = exception_name.rsplit(".", 1)
            module = importlib.import_module(module_name)
            return getattr(module, class_name)

        common_modules = [
            "requests.exceptions",
            "urllib.error",
            "urllib3.exceptions",
            "http.client",
            "socket",
            "os",
            "io",
        ]
        for module_name in common_modules:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, exception_name):
                    return getattr(module, exception_name)
            except ImportError:
                continue
        raise ImportError(f"Could not find exception class: {exception_name}")

    def to_dict(self) -> dict[str, Any]:
        """Convert RetryConfig to dictionary, properly handling exception classes.

        This ensures that exception classes are converted to their string names
        rather than their full string representation (e.g., "ValueError" instead of
        "<class 'ValueError'>").
        """
        data = super().to_dict()

        # Convert exception classes to their names for proper YAML serialization
        if isinstance(data.get("retry_exceptions"), list):
            converted_exceptions = []
            for exc in data["retry_exceptions"]:
                if (
                    isinstance(exc, str)
                    and exc.startswith("<class '")
                    and exc.endswith("'>")
                ):
                    # Extract the class name from the full string representation
                    class_name = exc[8:-2]  # Remove "<class '" and "'>"
                    converted_exceptions.append(class_name)
                else:
                    converted_exceptions.append(exc)
            data["retry_exceptions"] = converted_exceptions

        return data


class RunConfig(BaseConfig):
    inputs: dict | None = msgspec.field(default_factory=dict)
    final_vars: list[str] | None = msgspec.field(default_factory=list)
    config: dict | None = msgspec.field(default_factory=dict)
    cache: dict | bool | None = msgspec.field(default=False)
    with_adapter: WithAdapterConfig = msgspec.field(default_factory=WithAdapterConfig)
    executor: ExecutorConfig = msgspec.field(default_factory=ExecutorConfig)
    executor_override_raw: Any | None = msgspec.field(default=None)
    log_level: str | None = msgspec.field(default="INFO")
    # New nested retry configuration
    retry: RetryConfig | None = msgspec.field(default=None)
    # Deprecated top-level retry fields (kept for backward compatibility)
    max_retries: int = msgspec.field(default=3)
    retry_delay: int | float = msgspec.field(default=1)
    jitter_factor: float | None = msgspec.field(default=0.1)
    retry_exceptions: list[str] = msgspec.field(default_factory=lambda: ["Exception"])  # type: ignore[assignment]
    # New fields for comprehensive configuration
    pipeline_adapter_cfg: dict | None = msgspec.field(default=None)
    project_adapter_cfg: dict | None = msgspec.field(default=None)
    adapter: dict[str, Any] | None = msgspec.field(default=None)
    reload: bool = msgspec.field(default=False)
    on_success: CallbackSpec | None = msgspec.field(default=None)
    on_failure: CallbackSpec | None = msgspec.field(default=None)
    additional_modules: list[str | Any] | None = msgspec.field(default=None)

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        for field in DEPRECATED_RETRY_FIELDS:
            data.pop(field, None)
        retry_data = data.get("retry")
        if isinstance(retry_data, dict):
            exceptions: list[Any] = []
            if self.retry and isinstance(self.retry.retry_exceptions, list):
                for exc in self.retry.retry_exceptions:
                    if isinstance(exc, str):
                        exceptions.append(exc)
                    elif isinstance(exc, type) and issubclass(exc, BaseException):
                        exceptions.append(exc.__name__)
                    else:
                        exceptions.append(str(exc))
            else:
                raw_exceptions = retry_data.get("retry_exceptions", [])
                if isinstance(raw_exceptions, list):
                    for exc in raw_exceptions:
                        if isinstance(exc, str):
                            exceptions.append(exc)
                        elif isinstance(exc, type) and issubclass(exc, BaseException):
                            exceptions.append(exc.__name__)
                        else:
                            exceptions.append(str(exc))
            if exceptions:
                retry_data["retry_exceptions"] = exceptions

        modules = data.get("additional_modules")
        if modules is not None:
            serialised_modules: list[str] = []
            for module in modules:
                if isinstance(module, str):
                    serialised_modules.append(module)
                else:
                    serialised_modules.append(getattr(module, "__name__", str(module)))
            data["additional_modules"] = serialised_modules
        return data

    def __post_init__(self):
        legacy_overrides: dict[str, Any] = {}
        for field, default_value in _LEGACY_RETRY_DEFAULTS.items():
            current_value = getattr(self, field)
            if field == "retry_exceptions":
                def _normalise(values):
                    normalised: list[str] = []
                    iterable = values if isinstance(values, (list, tuple)) else [values]
                    for item in iterable:
                        if isinstance(item, str):
                            normalised.append(item)
                        elif isinstance(item, type) and issubclass(item, BaseException):
                            normalised.append(item.__name__)
                        else:
                            normalised.append(str(item))
                    return normalised

                if _normalise(current_value) != _normalise(default_value):
                    legacy_overrides[field] = current_value
            else:
                if current_value != default_value:
                    legacy_overrides[field] = current_value

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
            self.executor_override_raw = self.executor_override_raw or None
        if isinstance(self.pipeline_adapter_cfg, dict):
            from ..pipeline.adapter import AdapterConfig as PipelineAdapterConfig

            self.pipeline_adapter_cfg = PipelineAdapterConfig.from_dict(
                self.pipeline_adapter_cfg
            )
        if isinstance(self.project_adapter_cfg, dict):
            from ..project.adapter import AdapterConfig as ProjectAdapterConfig

            self.project_adapter_cfg = ProjectAdapterConfig.from_dict(
                self.project_adapter_cfg
            )
        if isinstance(self.adapter, dict):
            # Convert adapter instances if needed
            pass

        if self.additional_modules is not None:
            if isinstance(self.additional_modules, (str, bytes)):
                self.additional_modules = [self.additional_modules]
            elif not isinstance(self.additional_modules, list):
                self.additional_modules = list(self.additional_modules)  # type: ignore[arg-type]

        # Normalize retry configuration (prefer nested RetryConfig)
        if isinstance(self.retry, dict):
            self.retry = RetryConfig.from_dict(self.retry)
        if self.retry is None:
            # Build nested retry from (deprecated) top-level fields
            self.retry = RetryConfig(
                max_retries=self.max_retries,
                retry_delay=float(self.retry_delay),
                jitter_factor=self.jitter_factor,
                retry_exceptions=self.retry_exceptions,
            )
        # Keep top-level fields in sync for backward compatibility
        self.max_retries = self.retry.max_retries
        self.retry_delay = self.retry.retry_delay
        self.jitter_factor = self.retry.jitter_factor
        # Ensure top-level exceptions reflect converted classes
        self.retry_exceptions = list(self.retry.retry_exceptions)

        if legacy_overrides:
            warnings.warn(
                (
                    "RunConfig retry fields {fields} are deprecated; configure values via the nested "
                    "`retry` block instead."
                ).format(fields=", ".join(sorted(legacy_overrides))),
                DeprecationWarning,
                stacklevel=2,
            )

        # Handle callback conversions
        if self.on_success is not None and not isinstance(
            self.on_success, CallbackSpec
        ):
            if callable(self.on_success):
                self.on_success = CallbackSpec(func=self.on_success)
            elif isinstance(self.on_success, tuple) and len(self.on_success) == 3:
                func, args, kwargs = self.on_success
                self.on_success = CallbackSpec(func=func, args=args, kwargs=kwargs)
            else:
                self.on_success = None
                warnings.warn(
                    "Invalid on_success format, must be Callable or (Callable, args, kwargs)",
                    RuntimeWarning,
                )
        # Handle on_failure callback conversions (mirror on_success behavior)
        if self.on_failure is not None and not isinstance(
            self.on_failure, CallbackSpec
        ):
            if callable(self.on_failure):
                self.on_failure = CallbackSpec(func=self.on_failure)
            elif isinstance(self.on_failure, tuple) and len(self.on_failure) == 3:
                func, args, kwargs = self.on_failure
                self.on_failure = CallbackSpec(func=func, args=args, kwargs=kwargs)
            else:
                self.on_failure = None
                warnings.warn(
                    "Invalid on_failure format, must be Callable or (Callable, args, kwargs)",
                    RuntimeWarning,
                )
