import sys

from flowerpower.utils.filesystem import (
    FilesystemHelper,
    add_modules_path,
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
