"""
Provide Tools for FileS ystem Operations

                                    DependencyLevel.sstcore.data[0]
"""

__all__: list[str] = [
    "SstFile",
    #
    "SstFiles",
    "QueryRegisterMixin",
    "SstFileFilter",
    "FileScanMixin",
    "FileSyncMixin",
    "SstFileRegistry",
]

# TASK: ListRegister/Vault changed heavily
# - adapt to new setup and methods
# - think about wiring with pydantic
# - Composition: where, how, Builder?

from ._base import SstFiles
from ._file import SstFile
from ._query import FileQueryRegistry
from ._scan import FileScanMixin
from ._sync import FileSyncMixin


class SstFileRegistry(
    FileSyncMixin,
    FileScanMixin,
    FileQueryRegistry,
    SstFiles,
): ...
