import pytest

from flowerpower.utils.security import (
    SecurityError,
    validate_executor_type,
    validate_pipeline_name,
)


def test_validate_pipeline_name_allows_dotted_pipeline_names():
    assert validate_pipeline_name("analytics.daily_summary") == "analytics.daily_summary"


def test_validate_pipeline_name_strips_surrounding_whitespace():
    assert validate_pipeline_name("  analytics.daily_summary  ") == "analytics.daily_summary"


@pytest.mark.parametrize("name", ["analytics..daily", ".leading", "trailing.", "bad/name"])
def test_validate_pipeline_name_rejects_invalid_names(name):
    with pytest.raises(SecurityError):
        validate_pipeline_name(name)


@pytest.mark.parametrize("executor_type", ["synchronous", "local", "threadpool"])
def test_validate_executor_type_allows_supported_executors(executor_type):
    assert validate_executor_type(executor_type) == executor_type
