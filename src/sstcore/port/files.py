"""
How to track Files with composed Registries?

                                    DependencyLevel.sstcore.port[6]

"""

__all__: list[str] = [
    "SyncMode",
    #
    "File",
    "FileRegister",  # MERGE: with Query?
    "QueryRegister",
    "SyncRegister",
    "ScanRegister",
    #
    "ScanFiles",
    "Files",
]

from collections.abc import Iterator
from enum import auto
from pathlib import Path
from typing import Protocol, Self

from .filter import Filter, PathFiltering  # 4
from .register import ListRegister  # 5
from .scanner import FolderScanning  # 5
from .solid import EnumMode
from .tree import PathTree  # 0

type PathS = Path | list[Path]  # IDEA: Sequence|Iterable?


class SyncMode(EnumMode):
    """Conflict Resolution Strategy for PathGuard File Transfers"""

    INCREMENT = auto()
    OVERRIDE = auto()
    IGNORE = auto()


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


class FileFiltering[FileT: File](Filter[str, FileT], Protocol):
    def _fulfill(self, target: FileT) -> bool:
        """Filter Registry Files by their Keyword Sets"""


class FileRegister(Protocol):
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


class QueryRegister(Protocol):
    """Govern Files in Registry and on Disk"""

    def paths(self, resolve=False) -> set[Path]:
        """List all Local Paths inside Local Dir, resolve to global Path"""

    def resolve(self, file: File) -> Path:
        """Compose Root Dir of Registry and Local Path of File"""

    @property
    def names(self) -> list[str]:
        """Collect all file names (inkl. suffix)"""

    def by_name(self, name: str) -> list[File]:
        """Filter by filenames"""

    def confirmed(self, local_dir: Path | None = None) -> list[File]:
        """Check Status on Disk and provide confirmed Files"""

    def unconfirmed(self, local_dir: Path | None = None) -> list[File]:
        """Check Status on Disk and provide unconfirmed Files"""


class ScanRegister(Protocol):
    """Scanner / tree / reload logic (Scan). Prepares for SyncModes."""

    # TODO: Scanner as Field (same for Filter)
    # scanner: FolderScanning
    # filter: PathFiltering
    @property
    def scanner(self) -> FolderScanning: ...
    @property
    def filter(self) -> PathFiltering: ...
    # def setup_scanner(self, path_filter: PathFiltering) -> FolderScanning: ...
    # def get_scanner(self) -> FolderScanning: ...
    def scan_local_dir(self) -> list[Path]: ...
    def walk_from_root(self) -> Iterator[Path]: ...
    @classmethod
    def sprout_at(cls, scan_root: Path) -> Self: ...
    def attach_local_files(self, *, clear: bool = False) -> list[File]: ...
    def tree(self, root_name: str = "") -> PathTree: ...


class SyncRegister(Protocol):
    """Sync operations (mirror/absorb) using PathGuard (FileSync)."""

    mode: SyncMode

    def mirror_from_path(
        self, source: PathS, mode: SyncMode = SyncMode.IGNORE
    ) -> list[File]: ...

    def absorb_from_path(
        self, source: PathS, mode: SyncMode = SyncMode.IGNORE
    ) -> list[File]: ...

    def mirror_from_registry(
        self, external: Self, mode: SyncMode = SyncMode.IGNORE
    ) -> list[File]: ...

    def absorb_from_registry(
        self, external: Self, mode: SyncMode = SyncMode.INCREMENT
    ) -> list[File]: ...

    def clone_empty_registry(
        self,
        root_dir: Path,
        /,
        *,
        exclude: set[str] | None = None,
        add_to_exclude: set[str] | None = None,
        exclude_unset: bool = False,
    ) -> Self: ...


class ScanFiles[FileT: File](
    ScanRegister,
    QueryRegister,
    FileRegister,
    ListRegister[File],
    Protocol,
): ...


# TASK: ListRegister changed heavily, adapt to this


class Files(
    SyncRegister,
    ScanRegister,
    QueryRegister,
    FileRegister,
    ListRegister[File],
    Protocol,
): ...
