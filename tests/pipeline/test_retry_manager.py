from unittest.mock import MagicMock

import pytest

from flowerpower.cfg.pipeline.run import CallbackSpec
from flowerpower.pipeline.retry import RetryManager


@pytest.fixture
def anyio_backend():
    """Pin anyio backend to asyncio only (no trio)."""
    return "asyncio"


def test_retry_manager_calls_success_callback():
    success_cb = MagicMock()
    mgr = RetryManager(
        max_retries=1,
        retry_delay=0.1,
        jitter_factor=0.0,
        retry_exceptions=(Exception,),
    )

    result = mgr.execute(
        operation=lambda: "ok",
        on_success=success_cb,
        on_failure=None,
        context_name="test",
    )

    assert result == "ok"
    success_cb.assert_called_once_with("ok", None)


def test_retry_manager_calls_failure_callback():
    failure_cb = MagicMock()
    mgr = RetryManager(
        max_retries=0,
        retry_delay=0.1,
        jitter_factor=0.0,
        retry_exceptions=(ValueError,),
    )

    def boom():
        raise ValueError("boom")

    with pytest.raises(ValueError):
        mgr.execute(
            operation=boom,
            on_success=None,
            on_failure=failure_cb,
            context_name="test",
        )

    failure_cb.assert_called_once()
    args, kwargs = failure_cb.call_args
    assert args[0] is None
    assert isinstance(args[1], ValueError)


def test_retry_manager_calls_success_callback_spec():
    """Test that RetryManager correctly handles CallbackSpec for success callbacks."""
    mock_func = MagicMock()
    callback_spec = CallbackSpec(func=mock_func, args=("extra_arg",), kwargs={"key": "value"})
    
    mgr = RetryManager(
        max_retries=1,
        retry_delay=0.1,
        jitter_factor=0.0,
        retry_exceptions=(Exception,),
    )

    result = mgr.execute(
        operation=lambda: "ok",
        on_success=callback_spec,
        on_failure=None,
        context_name="test",
    )

    assert result == "ok"
    mock_func.assert_called_once_with("ok", None, "extra_arg", key="value")


def test_retry_manager_calls_failure_callback_spec():
    """Test that RetryManager correctly handles CallbackSpec for failure callbacks."""
    mock_func = MagicMock()
    callback_spec = CallbackSpec(func=mock_func, args=("extra_arg",), kwargs={"key": "value"})
    
    mgr = RetryManager(
        max_retries=0,
        retry_delay=0.1,
        jitter_factor=0.0,
        retry_exceptions=(ValueError,),
    )

    def boom():
        raise ValueError("boom")

    with pytest.raises(ValueError):
        mgr.execute(
            operation=boom,
            on_success=None,
            on_failure=callback_spec,
            context_name="test",
        )

    mock_func.assert_called_once()
    args, kwargs = mock_func.call_args
    assert args[0] is None
    assert isinstance(args[1], ValueError)
    assert args[2] == "extra_arg"
    assert kwargs == {"key": "value"}


def test_retry_manager_callback_spec_with_none_args_kwargs():
    """Test that CallbackSpec with None args/kwargs works correctly."""
    mock_func = MagicMock()
    callback_spec = CallbackSpec(func=mock_func, args=None, kwargs=None)
    
    mgr = RetryManager(
        max_retries=1,
        retry_delay=0.1,
        jitter_factor=0.0,
        retry_exceptions=(Exception,),
    )

    result = mgr.execute(
        operation=lambda: "ok",
        on_success=callback_spec,
        on_failure=None,
        context_name="test",
    )

    assert result == "ok"
    mock_func.assert_called_once_with("ok", None)


@pytest.mark.anyio
async def test_retry_manager_async_calls_success_callback_spec():
    """Test that async execute correctly handles CallbackSpec for success callbacks."""
    mock_func = MagicMock()
    callback_spec = CallbackSpec(func=mock_func, args=("extra",), kwargs={"foo": "bar"})
    
    mgr = RetryManager(
        max_retries=1,
        retry_delay=0.1,
        jitter_factor=0.0,
        retry_exceptions=(Exception,),
    )

    async def async_op():
        return "async_ok"

    result = await mgr.execute_async(
        operation=async_op,
        on_success=callback_spec,
        on_failure=None,
        context_name="test",
    )

    assert result == "async_ok"
    mock_func.assert_called_once_with("async_ok", None, "extra", foo="bar")


@pytest.mark.anyio
async def test_retry_manager_async_calls_failure_callback_spec():
    """Test that async execute correctly handles CallbackSpec for failure callbacks."""
    mock_func = MagicMock()
    callback_spec = CallbackSpec(func=mock_func, args=("extra",), kwargs={"foo": "bar"})
    
    mgr = RetryManager(
        max_retries=0,
        retry_delay=0.1,
        jitter_factor=0.0,
        retry_exceptions=(ValueError,),
    )

    async def async_boom():
        raise ValueError("async boom")

    with pytest.raises(ValueError):
        await mgr.execute_async(
            operation=async_boom,
            on_success=None,
            on_failure=callback_spec,
            context_name="test",
        )

    mock_func.assert_called_once()
    args, kwargs = mock_func.call_args
    assert args[0] is None
    assert isinstance(args[1], ValueError)
    assert args[2] == "extra"
    assert kwargs == {"foo": "bar"}
