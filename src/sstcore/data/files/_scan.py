"""
Provide Container for Files and Tools for FileSystem Operations

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "FileScanMixin",
]

from collections.abc import Callable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Self

from loguru import logger

from ...port.files import File, ScanRegister
from ...port.filter import PathFiltering, ProjectFiltering
from ...port.tree import PathTree
from ...util import FolderScanner
from ...util.filter import ProjectFilter
from ...util.tree import build_path_tree
from ._filter import FileFilter


class FileScanMixin:
    """Setup scanner, load directories and build tree"""

    root_dir: Path
    files: list[File]
    attach_from_path: Callable[[Path], File]
    filtered: Callable[[FileFilter | None], list[File]]
    clear: Callable[..., int]
    paths: Callable[..., set[Path]]

    scanner: FolderScanner | None = None

    @property
    def load_default_path_filter(self) -> PathFiltering:
        default_filter: ProjectFiltering = ProjectFilter()
        logger.info(f"Scanner Setup with Default Filter: {default_filter}")
        return default_filter

    def setup_scanner(
        self, path_filter: PathFiltering | None = None
    ) -> FolderScanner:
        filter: PathFiltering = (
            self.load_default_path_filter
            if path_filter is None
            else path_filter
        )
        self.scanner = FolderScanner(scan_root=self.root_dir, filter=filter)
        return self.scanner

    def get_scanner(self) -> FolderScanner:
        if not self.scanner:
            return self.setup_scanner()
        return self.scanner

    def scan_local_dir(self) -> list[Path]:
        scanner: FolderScanner = self.get_scanner()
        return scanner.get_files()

    def walk_from_root(self) -> Iterator[Path]:
        scanner: FolderScanner = self.get_scanner()
        yield from scanner.walk()

    @classmethod
    def sprout_at(cls, scan_root: Path) -> Self:
        """Establish Registy at target dir and create with all files scanned"""
        registry: Self = cls(root_dir=scan_root)  # ty:ignore
        registry.attach_local_files()
        return registry

    def attach_local_files(self, *, clear: bool = False) -> list[File]:
        """Scan nested root dir and attach new files, delete all with clear"""
        if clear:
            logger.info(f"Deleted {self.clear()} files")
        existing_paths: set[Path] = self.paths()
        return [
            self.attach_from_path(path)
            for path in self.walk_from_root()
            if path not in existing_paths
        ]

    def tree(  # LATER: create SstFileTree?
        self, root_name: str = "", file_filter: FileFilter | None = None
    ) -> PathTree:
        return build_path_tree(
            paths=[file.path for file in self.filtered(file_filter)],
            root_name=root_name or self.root_dir.name,
        )


if TYPE_CHECKING:
    _instance: ScanRegister = FileScanMixin.sprout_at(scan_root=Path.cwd())
    _class_check: type[ScanRegister] = FileScanMixin
