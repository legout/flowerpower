import sys

from flowerpower.utils.filesystem import (
    FilesystemHelper,
    add_modules_path,
    format_pipeline_file_path,
    format_pipeline_module_path,
    format_pipeline_package_root,
    get_pipeline_config_paths,
    get_project_config_paths,
    resolve_project_path,
)


class _DummyFS:
    is_cache_fs = False

    def __init__(self, path: str):
        self.path = path


class _DummyCacheFS:
    is_cache_fs = True

    def __init__(self, path: str | None = None):
        self.path = path
        self.sync_calls = 0

    def sync_cache(self) -> None:
        self.sync_calls += 1


class _BrokenMapperCacheFS(_DummyCacheFS):
    _mapper = object()


def test_add_modules_path_normalizes_empty_pipeline_dir() -> None:
    original = list(sys.path)
    try:
        sys.path[:] = []
        add_modules_path(_DummyFS("/tmp/project"), "", "/tmp/project")
        assert sys.path == ["/tmp/project"]
    finally:
        sys.path[:] = original


def test_add_modules_path_adds_distinct_nested_modules_path() -> None:
    original = list(sys.path)
    try:
        sys.path[:] = []
        add_modules_path(_DummyFS("/tmp/project/"), "pkg/flows", "/tmp/project")
        assert sys.path == ["/tmp/project/pkg/flows", "/tmp/project"]
    finally:
        sys.path[:] = original


def test_add_modules_path_does_not_duplicate_equivalent_project_path() -> None:
    original = list(sys.path)
    try:
        sys.path[:] = ["/tmp/project/"]
        add_modules_path(_DummyFS("/tmp/project"), "", "/tmp/project")
        assert sys.path == ["/tmp/project/"]
    finally:
        sys.path[:] = original


def test_resolve_project_path_falls_back_when_cache_fs_has_no_mapper_directory() -> None:
    fs = _BrokenMapperCacheFS("/tmp/project")

    assert resolve_project_path(fs, "/fallback") == "/tmp/project"
    assert fs.sync_calls == 1


def test_resolve_project_path_uses_base_dir_when_cache_fs_exposes_no_path() -> None:
    fs = _BrokenMapperCacheFS()

    assert resolve_project_path(fs, "/fallback") == "/fallback"
    assert fs.sync_calls == 1


def test_resolve_project_path_preserves_remote_urls() -> None:
    fs = _DummyFS("s3://bucket/project/")

    assert resolve_project_path(fs, "/fallback") == "s3://bucket/project"


def test_add_modules_path_skips_remote_urls() -> None:
    original = list(sys.path)
    try:
        sys.path[:] = []
        add_modules_path(_DummyFS("s3://bucket/project"), "pipelines", "s3://bucket/project")
        assert sys.path == []
    finally:
        sys.path[:] = original


# --- format_pipeline_* helpers ---


def test_format_pipeline_file_path_replaces_hyphens_with_underscores() -> None:
    assert format_pipeline_file_path("my-pipeline") == "my_pipeline"


def test_format_pipeline_file_path_replaces_dots_with_slashes() -> None:
    assert format_pipeline_file_path("sub.module") == "sub/module"


def test_format_pipeline_file_path_combined_dots_and_hyphens() -> None:
    assert format_pipeline_file_path("my-pipeline.sub") == "my_pipeline/sub"
    assert format_pipeline_file_path("a.b-c.d") == "a/b_c/d"


def test_format_pipeline_module_path_replaces_hyphens_only() -> None:
    assert format_pipeline_module_path("my-pipeline") == "my_pipeline"


def test_format_pipeline_module_path_preserves_dots() -> None:
    assert format_pipeline_module_path("sub.module") == "sub.module"
    assert format_pipeline_module_path("my-pipeline.sub") == "my_pipeline.sub"


def test_format_pipeline_package_root_converts_slashes_to_dots() -> None:
    assert format_pipeline_package_root("pipelines") == "pipelines"
    assert format_pipeline_package_root("pkg/flows") == "pkg.flows"


def test_format_pipeline_package_root_returns_empty_for_root() -> None:
    assert format_pipeline_package_root("") == ""
    assert format_pipeline_package_root(None) == ""


# --- config path helpers ---


def test_get_pipeline_config_paths_are_unique() -> None:
    paths = get_pipeline_config_paths(
        "demo",
        "",
        "",
        extensions=(".yml", ".yaml", ".yml"),
    )

    assert paths == ["demo.yml", "demo.yaml"]


def test_get_project_config_paths_are_unique() -> None:
    paths = get_project_config_paths(
        "",
        extensions=(".yml", ".yaml", ".yml"),
    )

    assert paths == ["project.yml", "project.yaml"]
