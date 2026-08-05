"""
Prepare Cascade of Filters

- FilterSet as Base for different purposes
                                                       DependencyLevel[2]
"""

__all__: list[str] = [
    "PathFilter",
    "ProjectFilter",
]

from dataclasses import dataclass, field
from pathlib import Path

from ._box import FilterBox
from ._set import FilterSet


@dataclass
class PathFilter(FilterSet[str, Path]):
    """Decomposes Paths and filter piece by piece in target set"""

    def _create_target_set(self, target: Path) -> set[str]:
        return set(target.parts) | {target.stem} | {target.suffix}


@dataclass
class ProjectFilter(PathFilter):
    """Reject unwanted Folders and include desired Files"""

    exclude: set[str] = field(
        default_factory=lambda: set(FilterBox.PROJECT.args.exclude)
    )
    require_any: set[str] = field(
        default_factory=lambda: set(FilterBox.PROJECT.args.require_any)
    )

    def _fulfills_conditions(self, target: Path, target_set: set[str]) -> bool:

        if not self.allow_hidden_files and target.name.startswith("."):
            return False
        if target.is_dir():
            return self.fulfills_exclude(target_set)
        if target.is_file():
            return self.fulfills_require_any(target_set)

        return False
