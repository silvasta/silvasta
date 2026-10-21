"""
Prepare Cascade of Filters

                                                       DependencyLevel[2]
"""

__all__: list[str] = [
    "FileFilter",
    "PathFilter",
    "ProjectFilter",
]

from dataclasses import dataclass, field
from pathlib import Path

from ...port.files import File
from ...port.filter import PathFiltering, ProjectFiltering
from ...port.link import portlink
from ._box import FilterArgs
from ._engine import FilterSet


class FileFilter[FileT: File](FilterSet[str, FileT]):
    def _fulfill(self, target: FileT) -> bool:
        return self.fulfills_trio(target_set=target.keywords)


@portlink(PathFiltering)
@dataclass
class PathFilter(FilterSet[str, Path]):
    def _fulfill(self, target: Path) -> bool:
        """Decompose Paths and filter by fragments"""
        return self.fulfills_trio(
            target_set=set(target.parts) | {target.stem} | {target.suffix}
        )


@portlink(ProjectFiltering)
@dataclass
class ProjectFilter(PathFilter):
    """Reject unwanted Folders and include desired Files"""

    exclude: set[str] = field(
        default_factory=lambda: FilterArgs.PROJECT().exclude
    )
    require_any: set[str] = field(
        default_factory=lambda: FilterArgs.PROJECT().require_any
    )

    def _fulfill(self, target: Path) -> bool:
        target_set: set[str] = (  # LATER: unite again with PathFilter
            set(target.parts) | {target.stem} | {target.suffix}
        )
        if not self.allow_hidden_files and target.name.startswith("."):
            return False
        if target.is_dir():
            return self.fulfills_exclude(target_set)
        if target.is_file():
            return self.fulfills_require_any(target_set)

        return False
