"""
Provide Tools for FileS ystem Operations

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "SstFile",
    #
    "SstFiles",
    "FileQueryMixin",
    "SstFileFilter",
    "FileFilterMixin",
    "FileScanMixin",
    "FileSyncMixin",
    "SstFileRegistry",
    #
    "RegistryBuilder",
]


from typing import TYPE_CHECKING

from ._base import SstFiles
from ._compose import RegistryBuilder, SstFileRegistry
from ._file import SstFile
from ._filter import FileFilterMixin
from ._query import FileQueryMixin
from ._scan import FileScanMixin
from ._sync import FileSyncMixin

if TYPE_CHECKING:
    from ...port.files import (
        FileFiltering,
        FileQuery,
        FileRegistry,
        Files,
        FileScanning,
        FileSyncing,
    )
    from ...port.registry import ListingRegistry

    class _ComposedFiles(
        SstFiles,
        FileQuery,
        FileFilterMixin,
        FileScanMixin,
        ListingRegistry[SstFile],
    ):
        pass

    _files_check: Files = _ComposedFiles()
    _query_check: FileQuery = _ComposedFiles()
    _filter_check: FileFiltering = _ComposedFiles()
    _scan_check: FileScanning = _ComposedFiles()
    _sync_check: FileSyncing = _ComposedFiles()
    _full_check: FileRegistry = _ComposedFiles()
