from unittest.mock import MagicMock

import pytest

from flowerpower.pipeline.retry import RetryManager


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
