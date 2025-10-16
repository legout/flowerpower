import pytest

from flowerpower.cfg.pipeline.run import ExecutorConfig
from flowerpower.utils.config import prefer_executor_override


def test_prefer_executor_override_string_type_overrides():
    base = ExecutorConfig(type="threadpool", max_workers=8, num_cpus=2)
    merged = prefer_executor_override(base, "synchronous")
    assert merged.type == "synchronous"
    # Unspecified fields fall back to base
    assert merged.max_workers == 8
    assert merged.num_cpus == 2


def test_prefer_executor_override_dict_explicit_fields():
    base = ExecutorConfig(type="threadpool", max_workers=8, num_cpus=2)
    # Explicitly set max_workers to 4
    merged = prefer_executor_override(base, {"max_workers": 4})
    assert merged.type == "threadpool"
    assert merged.max_workers == 4
    assert merged.num_cpus == 2


def test_prefer_executor_override_dict_none_clears_field():
    base = ExecutorConfig(type="processpool", max_workers=16, num_cpus=8)
    # Explicit None should clear the field (becoming None)
    merged = prefer_executor_override(base, {"max_workers": None})
    assert merged.type == "processpool"
    assert merged.max_workers is None
    assert merged.num_cpus == 8
