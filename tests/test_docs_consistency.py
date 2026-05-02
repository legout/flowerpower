"""Validate that docs remain consistent with the canonical RunConfigBuilder API."""

from pathlib import Path
import re


REPO_ROOT = Path(__file__).parents[1]
DOCS_FILES = [
    REPO_ROOT / "README.md",
    *sorted((REPO_ROOT / "docs").rglob("*.md")),
]


def _grep_files(pattern: str, files: list[Path]) -> list[str]:
    """Return lines matching pattern across files."""
    results = []
    for f in files:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), start=1):
            if re.search(pattern, line):
                results.append(f"{f}:{i}: {line.strip()}")
    return results


def test_no_legacy_import_in_docs():
    """AC3: docs must not reference the deprecated builder import path."""
    pattern = r"from\s+flowerpower\.cfg\.pipeline\.builder\s+import\s+RunConfigBuilder"
    matches = _grep_files(pattern, DOCS_FILES)
    assert not matches, "Legacy import found in docs:\n" + "\n".join(matches)


def test_no_phantom_builder_methods_in_docs():
    """AC3: docs must not reference method names that do not exist on the canonical builder."""
    phantom_methods = [
        "with_executor_config",
        "with_adapter_config",
        "with_pipeline_adapter_config",
        "with_project_adapter_config",
        "with_success_callback",
        "with_failure_callback",
    ]
    pattern = r"\b(" + "|".join(phantom_methods) + r")\b"
    matches = _grep_files(pattern, DOCS_FILES)
    assert not matches, "Phantom method names found in docs:\n" + "\n".join(matches)


def test_no_pipeline_name_constructor_in_readme_and_quickstart():
    """AC1: README and quickstart must not show RunConfigBuilder(pipeline_name=...)."""
    target_files = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "docs" / "quickstart.md",
    ]
    pattern = r"RunConfigBuilder\s*\(\s*pipeline_name\s*="
    matches = _grep_files(pattern, target_files)
    assert not matches, "pipeline_name= constructor found:\n" + "\n".join(matches)
