"""
Scan Folders, Files, ... parsed with(out) syntax and context grouping

-
"""

# IDEAS: Scanner
# - (Static) Master object, Scanner: unite functions like PathGuard

__all__: list[str] = [
    "FileExtractor",
]

from pathlib import Path
from typing import Protocol

from .view import Stringable


class FileExtractor(Protocol):
    """Define the Shape of the File extraction Engine"""

    def __call__(self, path: Path) -> Stringable:
        """Provide str or container object that produces str"""
