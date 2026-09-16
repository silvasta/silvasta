"""
Scan Folders, Files, ... parsed with(out) syntax and context grouping

                                                 DependencyLevel[2]
                                                          filter(1)
"""

__all__: list[str] = [
    "FolderScan",
    "FileScan",
    "ScanMode",
    # IDEAS:
    # "AstExtract",
    # "CstExtract",
    # "MarkdownExtract",
    # "PdfExtract",
]

from collections.abc import Iterator
from enum import StrEnum, auto
from pathlib import Path
from typing import Protocol

from .calling import Stringable
from .filter import PathFiltering
from .tree import PathTree


class FolderScan(Protocol):
    """Scans a directory with a PathFilter/ProjectFilter."""

    scan_root: Path
    filter: PathFiltering

    def get_files(self) -> list[Path]: ...
    def walk(self) -> Iterator[Path]: ...
    def tree(self) -> PathTree: ...


class FileScan(Protocol):
    """Define the Shape of the File extraction Engine"""

    def __call__(self, path: Path) -> Stringable:
        """Provide str or container object that produces str"""


# AI_FOCUS: I need setup that works for all scanner
class ScanMode(StrEnum):
    """Govern the exectuion modes of FileScanner"""

    READ = auto()
    AST = auto()
    FST = auto()  # file system tree
