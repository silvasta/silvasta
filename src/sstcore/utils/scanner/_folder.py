"""
Scan the Folder and provide the (filtered) Files

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "FolderScanner",
]


from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from ..filter import PathFilter, ProjectFilter
from ..path.guard import PathGuard
from ..tree import PathTreeNode, build_path_tree


@dataclass
class FolderScanner:
    """
    Scan the selected directory by walking the paths downwards

    Use any PathFilter-FilterSet to select folder- and filenames, for
    more precise filtering consider the PatternFilter with regex match.

    Get Paths, build PathTree or create a summary file.
    """

    scan_root: Path
    filter: PathFilter = field(default_factory=ProjectFilter)

    provide_relative_paths: bool = False
    follow_symlinks: bool = False

    def get_files(self) -> list[Path]:
        """Collect and Sort the walked Paths"""
        return sorted(self.walk())

    def walk(
        self,
    ) -> Iterator[Path]:
        """Yield File Paths that match the attached Filter"""

        for dirpath, dirnames, filenames in self._walk():
            dirnames[:] = [
                dir  # the rest is skipped next iteration
                for dir in dirnames
                if self.filter(dirpath / dir)
            ]

            for file in filenames:
                if self.filter(file_path := dirpath / file):
                    yield (
                        PathGuard.relative(file_path, self.scan_root)
                        if self.provide_relative_paths
                        else file_path
                    )

    def _walk(self):
        yield from self.scan_root.walk(follow_symlinks=self.follow_symlinks)

    def tree(self) -> PathTreeNode:
        """Build Connected Nodes from walked Paths"""

        return build_path_tree(
            paths=sorted(self.walk()), root_name=self.scan_root.name
        )
