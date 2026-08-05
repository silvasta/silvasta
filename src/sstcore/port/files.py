"""
Define the Shape of the File Tracker and the Composed Registry

-
"""

__all__: list[str] = [
    "File",
    "Files",
    "FileQuery",
    "FileFilter",
    "FileFiltering",
    "FileScanning",
    "FileScanRegistry",
]

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, Self

from ..port.filter import Filter, PathFiltering
from ..port.pathguard import PathGuard
from ..port.registry import ListingRegistry
from ..port.tree import PathTree


class File(Protocol):
    """Track File Location and Status"""

    @property
    def name(self) -> str: ...
    @property
    def keywords(self) -> set[str]:
        """Provide Identifier for filtering and information"""

    @property
    def path(self) -> Path:
        """Locate the File inside Local Dir (depending on purpose, global)"""

    def confirm_local_status(self, root_dir: Path) -> bool:
        """Compose global path and check if your File is still there"""


class Files(Protocol):
    """Govern Files in Registry and on Disk"""

    @property
    def root_dir(self) -> Path:
        """Define the Source of all Files"""

    @property
    def files(self) -> list[File]:
        """Provide alias for registry.items"""

    def ensure_path(self, path: Path) -> Path:
        """Confirm path exists and is inside root_dir"""

    def relative_to_root(self, path: Path, strict: bool = True) -> Path:
        """Calculate Relative Path to Root (ignore if already relative)"""

    def attach_from_path(self, path, strict=True) -> File:
        """Attach File that is already inside root_dir"""

    def create_local_file(self, path: Path, *, strict=True) -> File:
        """Ensure valid File ready to attach is created"""

    def _create_local_file(self, *_args, **_kwargs) -> File:
        """Subhook for derived Registry: File Constructor"""


class FileQuery(Protocol):
    """Govern Files in Registry and on Disk"""

    def paths(self, resolve=False) -> set[Path]:
        """List all Local Paths inside Local Dir, resolve to global Path"""

    def resolve(self, file: File) -> Path:
        """Compose Root Dir of Registry and Local Path of File"""

    @property
    def file_names(self) -> list[str]:
        """Collect all file names (inkl. suffix)"""

    def get_by_name(self, name: str) -> list[File]:
        """Filter by filenames"""

    def confirmed_files(self, local_dir: Path | None = None) -> list[File]:
        """Check Status on Disk and provide confirmed Files"""

    def unconfirmed_files(self, local_dir: Path | None = None) -> list[File]:
        """Check Status on Disk and provide unconfirmed Files"""


class FileFilter(Filter[str, File], Protocol):
    """Filter SstFiles by keywords"""

    def _create_target_set(self, target: File) -> set[str]: ...


class FileFiltering(Protocol):
    """Keyword-based filtering queries (FilterMixin)."""

    def set_filter(self, file_filter: FileFilter) -> None: ...
    def reset_filter(self) -> None: ...
    def get_by_filter(
        self, file_filter: FileFilter | None = None
    ) -> list[File]: ...
    def get_by_keyword(
        self, keywords: str | list[str] | set[str]
    ) -> list[File]: ...
    def get_files_with_all_keywords(
        self, keywords: list[str] | set[str]
    ) -> list[File]: ...


# MOVE:
# NEXT:
class FolderScanning(Protocol):
    """Scans a directory with a PathFilter/ProjectFilter."""

    scan_root: Path
    filter: PathFiltering

    def get_files(self) -> list[Path]: ...
    def walk(self) -> Iterator[Path]: ...
    def tree(self) -> PathTree: ...


class FileScanning(Protocol):
    """Scanner / tree / reload logic (ScanMixin). Prepares for SyncModes."""

    @property
    def scanner(self) -> FolderScanning | None: ...
    def setup_scanner(self, path_filter: PathFiltering) -> FolderScanning: ...
    def get_scanner(self) -> FolderScanning: ...
    def scan_local_dir(self) -> list[Path]: ...
    def walk_from_root(self) -> Iterator[Path]: ...
    @classmethod
    def sprout_at(cls, scan_root: Path) -> Self: ...
    def attach_local_files(self, *, clear: bool = False) -> list[File]: ...
    def tree(
        self, root_name: str = "", file_filter: FileFilter | None = None
    ) -> PathTree: ...


type _Source = Path | list[Path]
_Sync = PathGuard.SyncMode


class FileSyncing(Protocol):
    """Sync operations (mirror/absorb) using PathGuard (FileSyncMixin)."""

    sync_mode: PathGuard.SyncMode

    def clone_empty_registry(
        self,
        root_dir: Path,
        exclude: set[str] | None = None,
        add_to_exclude: set[str] | None = None,
        exclude_unset: bool = False,
    ) -> Self: ...

    def mirror_from_path(
        self, source: _Source, sync_mode: _Sync = _Sync.IGNORE
    ) -> list[File]: ...

    def absorb_from_path(
        self, source: _Source, sync_mode: _Sync = _Sync.IGNORE
    ) -> list[File]: ...

    def mirror_from_registry(
        self, external: Self, sync_mode: _Sync = _Sync.IGNORE
    ) -> list[File]: ...

    def absorb_from_registry(
        self, external: Self, sync_mode: _Sync = _Sync.INCREMENT
    ) -> list[File]: ...


class FileScanRegistry(
    Files,
    FileQuery,
    FileFiltering,
    FileScanning,
    ListingRegistry[File],
    Protocol,
): ...


class FileRegistry(
    Files,
    FileQuery,
    FileFiltering,
    FileScanning,
    FileSyncing,
    ListingRegistry[File],
    Protocol,
): ...
