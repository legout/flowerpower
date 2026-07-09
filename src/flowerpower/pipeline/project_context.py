"""Internal project runtime context for pipeline facade wiring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fsspeckit import AbstractFileSystem


@dataclass(frozen=True)
class ProjectRuntimeContext:
    """Runtime facts shared by pipeline facade components.

    This context intentionally carries only project runtime resources and path
    facts. Project configuration freshness remains owned by the registry/loader
    cache; loaders and facade components are not stored here.
    """

    fs: AbstractFileSystem
    base_dir: str
    storage_options: dict[str, Any] | Any
    cfg_dir: str
    pipelines_dir: str
    owns_filesystem: bool
