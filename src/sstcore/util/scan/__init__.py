"""
# Scanner - Detect the Target!

## FolderScanner

- Needs a Target Root and optional a FilterSet to Walk a directory
- Provides Paths, builds a PathTree or creates a SummaryFile.

## [FileScanner]

- Future project: detect the content of files

                                                       DependencyLevel[X]
"""

__all__: list[str] = [
    "FolderScanner",
    "FileScanner",
    "SummaryFile",
    "SummaryFileMachine",
]

from ._file import FileScanner
from ._folder import FolderScanner
from ._summary import SummaryFile, SummaryFileMachine

# LATER: SummaryFile, dataclass with list with lines and optional write path
