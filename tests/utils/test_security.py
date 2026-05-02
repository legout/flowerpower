import pytest

from flowerpower.utils.security import (
    SecurityError,
    validate_directory_fragment,
    validate_executor_type,
    validate_file_path,
    validate_pipeline_name,
)

# --- validate_pipeline_name ---


def test_validate_pipeline_name_allows_dotted_pipeline_names():
    assert validate_pipeline_name("analytics.daily_summary") == "analytics.daily_summary"


def test_validate_pipeline_name_strips_surrounding_whitespace():
    assert validate_pipeline_name("  analytics.daily_summary  ") == "analytics.daily_summary"


@pytest.mark.parametrize("name", ["analytics..daily", ".leading", "trailing.", "bad/name"])
def test_validate_pipeline_name_rejects_invalid_names(name):
    with pytest.raises(SecurityError):
        validate_pipeline_name(name)


# --- validate_file_path ---


def test_validate_file_path_accepts_safe_relative_path():
    result = validate_file_path("pipelines/my_pipeline.yml")
    assert result == "pipelines/my_pipeline.yml"


def test_validate_file_path_accepts_safe_absolute_path():
    result = validate_file_path("/tmp/project/pipelines/my_pipeline.yml")
    assert result == "/tmp/project/pipelines/my_pipeline.yml"


def test_validate_file_path_rejects_traversal():
    with pytest.raises(SecurityError):
        validate_file_path("../etc/passwd")
    with pytest.raises(SecurityError):
        validate_file_path("pipelines/../../secret.yml")


def test_validate_file_path_rejects_dangerous_characters():
    with pytest.raises(SecurityError):
        validate_file_path("pipelines/my_pipeline; rm -rf /")
    with pytest.raises(SecurityError):
        validate_file_path("pipelines/my_pipeline | cat")
    with pytest.raises(SecurityError):
        validate_file_path("pipelines/my_pipeline`id`")


def test_validate_file_path_rejects_empty_path():
    with pytest.raises(ValueError):
        validate_file_path("")


def test_validate_file_path_rejects_absolute_when_not_allowed():
    with pytest.raises(SecurityError):
        validate_file_path("/tmp/project.yml", allow_absolute=False)


def test_validate_file_path_rejects_relative_when_not_allowed():
    with pytest.raises(SecurityError):
        validate_file_path("project.yml", allow_relative=False)


def test_validate_file_path_validates_extension():
    assert validate_file_path("project.yml", allowed_extensions=[".yml", ".yaml"]) == "project.yml"
    with pytest.raises(SecurityError):
        validate_file_path("project.txt", allowed_extensions=[".yml", ".yaml"])


# --- validate_directory_fragment ---


def test_validate_directory_fragment_preserves_none():
    assert validate_directory_fragment(None) is None


def test_validate_directory_fragment_preserves_empty_string():
    assert validate_directory_fragment("") == ""


def test_validate_directory_fragment_accepts_safe_relative_fragment():
    assert validate_directory_fragment("pipelines") == "pipelines"
    assert validate_directory_fragment("pkg/flows") == "pkg/flows"


def test_validate_directory_fragment_rejects_traversal():
    with pytest.raises(SecurityError):
        validate_directory_fragment("../secret")


def test_validate_directory_fragment_rejects_absolute():
    with pytest.raises(SecurityError):
        validate_directory_fragment("/tmp/pipelines")


# --- validate_executor_type ---


@pytest.mark.parametrize("executor_type", ["synchronous", "local", "threadpool"])
def test_validate_executor_type_allows_supported_executors(executor_type):
    assert validate_executor_type(executor_type) == executor_type
