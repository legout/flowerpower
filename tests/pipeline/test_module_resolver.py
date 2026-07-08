from types import ModuleType
from unittest.mock import patch

from flowerpower.pipeline.module_resolver import PipelineModuleResolver


def test_resolver_prefers_configured_package_and_normalizes_hyphens() -> None:
    resolver = PipelineModuleResolver("flows")
    module = ModuleType("flows.my_pipeline")
    attempted: list[str] = []

    def fake_load(name: str, reload: bool = False):
        attempted.append(name)
        if name == "flows.my_pipeline":
            return module
        raise ImportError(name)

    with patch(
        "flowerpower.pipeline.module_resolver.load_module", side_effect=fake_load
    ):
        result = resolver.load("my-pipeline")

    assert result is module
    assert attempted == ["flows.my_pipeline"]


def test_resolver_error_lists_attempted_candidates() -> None:
    resolver = PipelineModuleResolver("flows")

    def fake_missing(name: str, reload: bool = False):
        raise ModuleNotFoundError(f"No module named {name!r}", name=name)

    with patch(
        "flowerpower.pipeline.module_resolver.load_module",
        side_effect=fake_missing,
    ):
        try:
            resolver.load("missing-pipeline")
        except ImportError as exc:
            message = str(exc)
        else:  # pragma: no cover - defensive assertion
            raise AssertionError("expected ImportError")
    assert "Tried" in message
    assert "flows.missing_pipeline" in message
    assert "missing-pipeline" in message
    assert "missing_pipeline" in message
    assert "pipelines.missing_pipeline" in message


def test_resolver_keeps_unique_modules_in_order() -> None:
    resolver = PipelineModuleResolver("pipelines")
    setup = ModuleType("pipelines.setup")
    primary = ModuleType("pipelines.primary")

    result = resolver.resolve(primary, additional=[setup, setup])

    assert result == [setup, primary]


def test_resolver_reloads_module_objects_when_requested() -> None:
    resolver = PipelineModuleResolver("pipelines")
    module = ModuleType("pipelines.setup")

    with patch(
        "flowerpower.pipeline.module_resolver.importlib.reload"
    ) as reload_module:
        result = resolver.coerce(module, reload=True)

    assert result is module
    reload_module.assert_called_once_with(module)


def test_resolver_respects_explicit_dotted_additional_imports() -> None:
    resolver = PipelineModuleResolver("flows")
    external_module = ModuleType("external.setup")
    package_relative_module = ModuleType("flows.external.setup")
    primary_module = ModuleType("flows.primary")

    def fake_load(name: str, reload: bool = False):
        if name == "external.setup":
            return external_module
        if name == "flows.external.setup":
            return package_relative_module
        raise ModuleNotFoundError(f"No module named {name!r}", name=name)

    with patch(
        "flowerpower.pipeline.module_resolver.load_module", side_effect=fake_load
    ):
        result = resolver.resolve(primary_module, additional=["external.setup"])

    assert result == [external_module, primary_module]


def test_resolver_does_not_fallback_after_internal_import_error() -> None:
    resolver = PipelineModuleResolver("pipelines")
    fallback_module = ModuleType("demo")

    def fake_load(name: str, reload: bool = False):
        if name == "pipelines.demo":
            raise ModuleNotFoundError(
                "No module named 'definitely_missing_dep_xyz'",
                name="definitely_missing_dep_xyz",
            )
        if name == "demo":
            return fallback_module
        raise ModuleNotFoundError(f"No module named {name!r}", name=name)

    with patch(
        "flowerpower.pipeline.module_resolver.load_module", side_effect=fake_load
    ):
        try:
            resolver.load("demo")
        except ModuleNotFoundError as exc:
            assert exc.name == "definitely_missing_dep_xyz"
        else:  # pragma: no cover - defensive assertion
            raise AssertionError("expected internal import failure to be re-raised")


def test_resolver_reloads_duplicate_modules_once_after_deduplication() -> None:
    resolver = PipelineModuleResolver("pipelines")
    module = ModuleType("pipelines.setup")

    with patch(
        "flowerpower.pipeline.module_resolver.importlib.reload"
    ) as reload_module:
        result = resolver.resolve(module, additional=[module], reload=True)

    assert result == [module]
    reload_module.assert_called_once_with(module)
