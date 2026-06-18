from dataclasses import dataclass, field
from pathlib import Path

from ..log.inspect import debug_log_or_print
from .set import FilterSet


@dataclass
class PathFilter(FilterSet[str, Path]):
    """Modified Target Set that decomposes Paths."""

    def _create_target_set(self, target: Path) -> set[str]:
        return set(target.parts) | {target.stem} | {target.suffix}


PROJECT_IGNORE_DIRS: set[str] = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "target",
}


PROJECT_ALLOWED_EXTS: set[str] = {
    ".py",
    ".pyi",
    ".rs",
    ".md",
    ".json",
    ".yaml",
    ".toml",
    ".tex",
    ".cls",
    ".lua",
}


@dataclass
class ProjectFilter(PathFilter):
    """Setup with Defaults for Files of Projects"""

    exclude: set[str] = field(
        default_factory=lambda: set(PROJECT_IGNORE_DIRS),
    )
    require_any: set[str] = field(
        default_factory=lambda: set(PROJECT_ALLOWED_EXTS)
    )

    @debug_log_or_print(anyway=False)
    def _fulfills_conditions(self, target: Path, target_set: set) -> bool:

        if not self.allow_hidden_files and target.name.startswith("."):
            return False
        if target.is_dir():
            return self.fulfills_exclude(target_set)
        if target.is_file():
            return self.fulfills_require_any(target_set)

        return False
