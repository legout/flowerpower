"""Shared resolver for pipeline module imports.

Centralizes package-root normalization, fallback candidate generation,
hyphen-to-underscore handling, reload, and duplicate module removal so that the
registry, runner, and visualizer share one import policy.
"""

from __future__ import annotations

import importlib
from types import ModuleType

from ..settings import PIPELINES_DIR
from ..utils.filesystem import (
    format_pipeline_module_path,
    format_pipeline_package_root,
)
from ..utils.misc import load_module

__all__ = ["PipelineModuleResolver"]


class PipelineModuleResolver:
    """Resolve pipeline modules through a single shared import policy.

    Owns:

    * package-root normalization (``pipelines_dir`` -> dotted package root)
    * fallback candidate generation (package root, raw name,
      hyphen-normalized name, and a ``pipelines.<name>`` fallback)
    * hyphen-to-underscore handling (via ``format_pipeline_module_path``)
    * reload semantics (inline reload during resolution)
    * duplicate module removal (ordered, identity-based)
    * error messages listing every attempted candidate
    """

    def __init__(self, pipelines_dir: str | None = None) -> None:
        self._pipelines_dir = pipelines_dir
        self._package_root = format_pipeline_package_root(pipelines_dir)

    @property
    def package_root(self) -> str:
        """Normalized dotted package root derived from ``pipelines_dir``."""
        return self._package_root

    def load(
        self,
        name: str,
        *,
        reload: bool = False,
        package_relative: bool = True,
    ) -> ModuleType:
        """Import a single module, trying every fallback candidate.

        Args:
            name: Pipeline or module name (may contain hyphens or dots).
            reload: Whether to reload the module when already imported.
            package_relative: Whether dotted names should be tried under the
                configured pipeline package before being treated as explicit
                import paths. Primary pipeline names use ``True``; additional
                module names use ``False`` so explicit dotted imports are
                respected.

        Returns:
            The loaded :class:`~types.ModuleType`.

        Raises:
            ImportError: When no candidate can be imported. The message lists
                every candidate that was attempted. Import errors raised from
                inside a found module are re-raised instead of falling through
                to lower-priority candidates.
        """
        candidates = self._candidates(name, package_relative=package_relative)
        errors: list[ImportError] = []
        for candidate in candidates:
            try:
                return load_module(candidate, reload=reload)
            except ModuleNotFoundError as error:
                if not self._is_candidate_miss(candidate, error):
                    raise
                errors.append(error)
            except ImportError:
                raise

        raise ImportError(
            f"Could not import module '{name}'. Tried: {candidates}"
        ) from (errors[-1] if errors else None)

    def coerce(
        self,
        entry: str | ModuleType,
        *,
        reload: bool = False,
        package_relative: bool = False,
    ) -> ModuleType:
        """Return a module for a name string or an existing module object.

        Args:
            entry: A module name string or an already-loaded module object.
            reload: Whether to reload the module.
            package_relative: Whether dotted strings should be preferred under
                the configured pipeline package before their explicit path.

        Raises:
            TypeError: When ``entry`` is neither a string nor a module.
        """
        if isinstance(entry, ModuleType):
            if reload:
                importlib.reload(entry)
            return entry
        if isinstance(entry, str):
            return self.load(
                entry,
                reload=reload,
                package_relative=package_relative,
            )
        raise TypeError(
            "additional_modules entries must be module objects or import strings"
        )

    def resolve(
        self,
        primary: str | ModuleType,
        *,
        additional: list[str | ModuleType] | None = None,
        reload: bool = False,
    ) -> list[ModuleType]:
        """Resolve the primary module plus optional additional modules.

        Additional modules are placed first in the returned list, followed by
        the primary module. Duplicates are removed by identity while preserving
        the first-seen order.

        Args:
            primary: Primary pipeline name or module object.
            additional: Optional additional modules (names or objects).
            reload: Whether to reload every resolved module.

        Returns:
            Ordered list of unique modules.
        """
        modules: list[ModuleType] = []

        def _append_unique(module_obj: ModuleType) -> None:
            if any(existing is module_obj for existing in modules):
                return
            modules.append(module_obj)

        for entry in additional or []:
            _append_unique(self.coerce(entry, reload=False))
        _append_unique(self.coerce(primary, reload=False, package_relative=True))

        if reload:
            self._reload_unique(modules)
        return modules

    def _candidates(self, name: str, *, package_relative: bool) -> list[str]:
        """Build the ordered list of import candidates for ``name``."""
        formatted = format_pipeline_module_path(name)
        package_root = self._package_root
        candidates: list[str] = []

        if package_root and not formatted.startswith(f"{package_root}."):
            if package_relative or "." not in formatted:
                candidates.append(f"{package_root}.{formatted}")
        for candidate in (name, formatted):
            if candidate not in candidates:
                candidates.append(candidate)
        if package_root != PIPELINES_DIR and not formatted.startswith(
            f"{PIPELINES_DIR}."
        ):
            if package_relative or "." not in formatted:
                candidates.append(f"{PIPELINES_DIR}.{formatted}")

        return candidates

    def _reload_unique(self, modules: list[ModuleType]) -> None:
        """Reload each already de-duplicated module once."""
        for module in modules:
            importlib.reload(module)

    @staticmethod
    def _is_candidate_miss(candidate: str, error: ModuleNotFoundError) -> bool:
        """Return true when ``error`` means ``candidate`` itself is absent."""
        missing_name = error.name
        if not missing_name:
            return False
        return candidate == missing_name or candidate.startswith(f"{missing_name}.")
