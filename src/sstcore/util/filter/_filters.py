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
from typing import TYPE_CHECKING

from ...port.files import File, FileFiltering
from ...port.filter import PathFiltering, ProjectFiltering
from ._box import FilterBox
from ._set import FilterSet


class FileFilter(FilterSet[str, File]):
    def _fulfill(self, target: File) -> bool:
        """Filter SstFiles by their keywords set"""
        return self.fulfills_trio(target_set=target.keywords)


@dataclass
class PathFilter(FilterSet[str, Path]):
    def _fulfill(self, target: Path) -> bool:
        """Decompose Paths and filter by fragments"""
        return self.fulfills_trio(
            target_set=set(target.parts) | {target.stem} | {target.suffix}
        )


@dataclass
class ProjectFilter(PathFilter):
    """Reject unwanted Folders and include desired Files"""

    exclude: set[str] = field(
        default_factory=lambda: set(FilterBox.PROJECT.args.exclude)
    )
    require_any: set[str] = field(
        default_factory=lambda: set(FilterBox.PROJECT.args.require_any)
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


if TYPE_CHECKING:
    _instance: FileFiltering = FileFilter()
    _class: type[FileFiltering] = FileFilter
    #
    _instance: PathFiltering = PathFilter()
    _class: type[PathFiltering] = PathFilter
    #
    _instance: ProjectFiltering = ProjectFilter()
    _class: type[ProjectFiltering] = ProjectFilter
