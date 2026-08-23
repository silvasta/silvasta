"""
Scan File Content

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "FileExtractor",
    "ScanMode",
    "FileScanner",
]

from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path

from loguru import logger

from ...port.scanner import FileExtractor
from ..path.guard import PathGuard


class ScanMode(StrEnum):
    # MOVE: port (when the enum import hack actually works)
    """Govern the exectuion modes of FileScanner"""

    RAW = auto()
    AST = auto()

    @property
    def extractor(self) -> FileExtractor:
        """Provide the right tool for the right task"""
        match self:
            case ScanMode.AST:
                # TASK: return ast_api_extractor
                return raw_content_extractor
            case ScanMode.RAW:
                return raw_content_extractor


@dataclass
class FileScanner:
    """
    Scan the selected files and extrac the desired content

    Use any FileExtractor starting from the simple Reader to
    more precise information extracted from Ast.

    """

    files: list[Path]
    local_root: Path
    scan_mode: ScanMode = ScanMode.RAW

    def split_paths(self) -> Iterator[tuple[Path, Path]]:
        """Create Pair of absolute and relative Path for all files"""
        for target in self.files:  # LATER: make this directly in PathGuard
            read_path, show_path = PathGuard.split(target, self.local_root)
            if not read_path.is_file():
                continue
            yield read_path, show_path

    def file_scan(self) -> Iterator[tuple[str, Path]]:
        """Scan all files by mode, skip fails and yield extracted results"""

        for read_path, show_path in self.split_paths():
            try:
                text: str = self.scan_mode.extractor(read_path)
            except (UnicodeDecodeError, OSError) as error:
                logger.debug(f"skip {read_path}: {error}")
                continue

            yield text, show_path


def raw_content_extractor(path: Path) -> str:
    """Default: Just read the file contents."""
    return path.read_text(encoding="utf-8")
