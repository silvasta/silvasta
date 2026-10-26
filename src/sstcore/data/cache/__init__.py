"""
Store Data in Temporary Location

- scanner: Provide the FolderScanner with persistent local storage

                                    DependencyLevel.sstcore.data[0]
"""

__all__: list[str] = [
    "DiskScanCache",
]
from ._scanner import DiskScanCache
