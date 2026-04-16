"""Retry helper utilities for pipeline execution."""

from __future__ import annotations

import datetime as dt
import random
import time
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Tuple, Type

import humanize

from loguru import logger

if TYPE_CHECKING:
    from ..cfg.pipeline.run import CallbackSpec


class RetryManager:
    """Encapsulates retry and backoff behaviour for pipeline runs."""

    def __init__(
        self,
        *,
        max_retries: int,
        retry_delay: float,
        jitter_factor: float,
        retry_exceptions: Tuple[Type[BaseException], ...],
        sleep: Callable[[float], None] = time.sleep,
        rng: Callable[[], float] = random.random,
    ) -> None:
        self._max_retries = max(0, max_retries)
        self._retry_delay = max(0.0, retry_delay)
        self._jitter_factor = max(0.0, jitter_factor)
        self._retry_exceptions = retry_exceptions or (Exception,)
        self._sleep = sleep
        self._rng = rng

    def execute(
        self,
        *,
        operation: Callable[[], Any],
        on_success: Callable[..., Any] | None,
        on_failure: Callable[..., Any] | None,
        context_name: str,
    ) -> Any:
        """Execute the provided callable with retries."""
        start_time = dt.datetime.now()

        for attempt in range(self._max_retries + 1):
            try:
                logger.info(
                    "🚀 Running pipeline '{name}' (attempt {attempt}/{total})",
                    name=context_name,
                    attempt=attempt + 1,
                    total=self._max_retries + 1,
                )
                result = operation()
                self._handle_success(on_success, result)
                self._log_success(context_name, start_time)
                return result
            except self._retry_exceptions as error:  # type: ignore[arg-type]
                if attempt < self._max_retries:
                    delay = self._retry_delay * (2**attempt)
                    jitter = delay * self._jitter_factor * self._rng()
                    total_delay = delay + jitter

                    logger.warning(
                        "⚠️  Pipeline '{name}' failed (attempt {attempt}/{total}): {error}",
                        name=context_name,
                        attempt=attempt + 1,
                        total=self._max_retries + 1,
                        error=error,
                    )
                    logger.info(
                        "🔄 Retrying in {delay:.2f} seconds...",
                        delay=total_delay,
                    )
                    self._sleep(total_delay)
                    continue

                self._handle_failure(on_failure, error)
                self._log_failure(context_name, start_time, error, attempts=attempt)
                raise
            except Exception as error:
                self._handle_failure(on_failure, error)
                self._log_failure(context_name, start_time, error, attempts=attempt)
                raise

        # Should be unreachable
        raise RuntimeError("Retry manager exited without returning result.")

    async def execute_async(
        self,
        *,
        operation: Callable[[], Awaitable[Any]],
        on_success: Callable[..., Any] | None,
        on_failure: Callable[..., Any] | None,
        context_name: str,
    ) -> Any:
        """Async variant of execute with identical retry semantics."""
        start_time = dt.datetime.now()

        for attempt in range(self._max_retries + 1):
            try:
                logger.info(
                    "🚀 Running pipeline '{name}' (attempt {attempt}/{total})",
                    name=context_name,
                    attempt=attempt + 1,
                    total=self._max_retries + 1,
                )
                result = await operation()
                self._handle_success(on_success, result)
                self._log_success(context_name, start_time)
                return result
            except self._retry_exceptions as error:  # type: ignore[arg-type]
                if attempt < self._max_retries:
                    delay = self._retry_delay * (2**attempt)
                    jitter = delay * self._jitter_factor * self._rng()
                    total_delay = delay + jitter

                    logger.warning(
                        "⚠️  Pipeline '{name}' failed (attempt {attempt}/{total}): {error}",
                        name=context_name,
                        attempt=attempt + 1,
                        total=self._max_retries + 1,
                        error=error,
                    )
                    logger.info(
                        "🔄 Retrying in {delay:.2f} seconds...",
                        delay=total_delay,
                    )
                    await self._sleep_async(total_delay)
                    continue

                self._handle_failure(on_failure, error)
                self._log_failure(context_name, start_time, error, attempts=attempt)
                raise
            except Exception as error:
                self._handle_failure(on_failure, error)
                self._log_failure(context_name, start_time, error, attempts=attempt)
                raise

        raise RuntimeError("Retry manager exited without returning result.")

    async def _sleep_async(self, delay: float) -> None:
        import asyncio

        await asyncio.sleep(delay)

    @staticmethod
    def _is_callback_spec(callback: Any) -> bool:
        """Check if callback is a CallbackSpec instance.

        CallbackSpec is a msgspec.Struct with func, args, kwargs fields.
        It is NOT callable, unlike a raw callback function.
        """
        # Check if it's not callable (CallbackSpec is a struct, not a function)
        # but has the attributes that define a CallbackSpec
        if callable(callback):
            return False
        return hasattr(callback, "func") and hasattr(callback, "args") and hasattr(callback, "kwargs")

    @staticmethod
    def _handle_success(callback: Any, result: Any) -> None:
        """Handle success callback execution.
        
        Supports both raw callables and CallbackSpec objects.
        """
        if callback is None:
            return
        
        try:
            if RetryManager._is_callback_spec(callback):
                # CallbackSpec: call func(result, None, *args, **kwargs)
                args = callback.args or ()
                kwargs = callback.kwargs or {}
                callback.func(result, None, *args, **kwargs)
            else:
                # Raw callable: call callback(result, None)
                callback(result, None)
        except Exception as callback_error:  # pragma: no cover - defensive
            logger.error("Success callback failed: {error}", error=callback_error)

    @staticmethod
    def _handle_failure(callback: Any, error: Exception) -> None:
        """Handle failure callback execution.
        
        Supports both raw callables and CallbackSpec objects.
        """
        if callback is None:
            return
        
        try:
            if RetryManager._is_callback_spec(callback):
                # CallbackSpec: call func(None, error, *args, **kwargs)
                args = callback.args or ()
                kwargs = callback.kwargs or {}
                callback.func(None, error, *args, **kwargs)
            else:
                # Raw callable: call callback(None, error)
                callback(None, error)
        except Exception as callback_error:  # pragma: no cover - defensive
            logger.error("Failure callback failed: {error}", error=callback_error)

    @staticmethod
    def _log_success(context_name: str, start_time: dt.datetime) -> None:
        duration = humanize.naturaldelta(dt.datetime.now() - start_time)
        logger.success(
            "✅ Pipeline '{name}' completed successfully in {duration}",
            name=context_name,
            duration=duration,
        )

    @staticmethod
    def _log_failure(
        context_name: str,
        start_time: dt.datetime,
        error: Exception,
        *,
        attempts: int,
    ) -> None:
        duration = humanize.naturaldelta(dt.datetime.now() - start_time)
        logger.error(
            "❌ Pipeline '{name}' failed after {attempts} attempts in {duration}: {error}",
            name=context_name,
            attempts=attempts + 1,
            duration=duration,
            error=error,
        )
