"""
Scan Folders, Files, ... parsed with(out) syntax and context grouping

                                                 DependencyLevel[5]
"""

__all__: list[str] = [
    "FolderScanning",
    "FileScanning",
    "ScanMode",
    # IDEAS:
    # "AstExtract",
    # "CstExtract",
    # "MarkdownExtract",
    # "PdfExtract",
    "PresetInfo",
    "ScanCaching",
]

from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto
from pathlib import Path
from typing import ClassVar, Protocol, Self, runtime_checkable

from .filter import PathFiltering  # 4
from .represent import Stringable  # 0
from .tree import PathTree  # 0


class FolderScanning(Protocol):
    """Scans a directory with a PathFilter/ProjectFilter."""

    scan_root: Path
    filter: PathFiltering

    def get_files(self) -> list[Path]: ...
    def walk(self) -> Iterator[Path]: ...
    def tree(self) -> PathTree: ...


class FileScanning(Protocol):
    """Define the Shape of the File extraction Engine"""

    def __call__(self, path: Path) -> Stringable:
        """Provide str or container object that produces str"""


# TASK: setup that works for all scanner
class ScanMode(StrEnum):
    """Govern the execution modes of FileScanningner"""

    READ = auto()
    AST = auto()
    FST = auto()  # file system tree


@dataclass(frozen=True, slots=True)
class PresetInfo:
    """Metadata for Preset Selection ("selection of selection")"""

    name: str
    paths: tuple[Path, ...]
    updated_at: datetime | None = None

    @property
    def count(self) -> int:
        return len(self.paths)

    @property
    def is_last(self) -> bool:
        return self.name == "__last__"


@runtime_checkable
class ScanCaching(Protocol):
    """Store and Provide Scanner Path-Selections and Presets"""

    LAST: ClassVar[str] = "__last__"

    @property
    def scan_root(self) -> Path:
        """Cache Location in FileSystem"""

    def load(self, name: str = LAST) -> list[Path]:
        """Load existing Preset if exists and readable"""

    def save(
        self,
        selected: Iterable[Path],
        name: str = LAST,
        *,
        update_last: bool = True,
    ) -> None:
        """Save Path Selection (as next default for update_last=True)"""

    def exists(self, name: str = LAST) -> bool:  # CHECK: __contains__ ?
        """Check if Preset (or last selection) exists for current scan_root"""

    def names(self, *, include_last: bool = False) -> Sequence[str]:
        """Show available preset names"""

    def presets(self, *, include_last: bool = False) -> dict[str, PresetInfo]:
        """
        Provide full preset records mapped by preset name

        - Idea: use for preset-picker TUI before launching TreeSelector on files
        """

    def delete(self, name: str) -> bool:  # Register.clear(key)
        """Delete one preset by name and confirm success"""

    def clear(self) -> int:  # Register.clear(key)
        """Delete all presets and count"""

    def prune(self) -> int:
        """Remove non-existent files from stored presets and count"""
        ...

    def close(self) -> None:
        """Release any underlying resources"""

    def __enter__(self) -> Self:
        """Ensure everything ready"""

    def __exit__(self, _type, error: BaseException | None, _tb) -> None:
        # LATER: change None if ever intended to handle something
        """Ensure everything saved and released"""
