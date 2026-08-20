"""
Provide Container for Files and Tools for FileSystem Operations

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "FileFilterMixin",
]


from typing import TYPE_CHECKING

from ...brick.registry import ListRegistry
from ...port.files import File, FileFilter, FileFiltering

type KeyWords = str | list[str] | set[str]


class FileFilterMixin(ListRegistry[File]):
    """Provide Keyword filtering"""

    def set_filter(self, file_filter: FileFilter) -> None:
        """Install new custom FileFilter"""
        self.filter: FileFilter = file_filter

    def reset_filter(self) -> None:
        """Shutdown Filter"""
        self.filter = None

    def get_by_filter(
        self, file_filter: FileFilter | None = None
    ) -> list[File]:
        """Get all files filtered by keywords setup in file_filter"""
        return self.filtered(file_filter)

    def get_by_keyword(self, keywords: KeyWords) -> list[File]:
        """Get all files that have at least 1 of the required keywords"""
        keyword_filter = SstFileFilter(require_any=set(keywords))
        return keyword_filter(self.all)

    def get_files_with_all_keywords(self, keywords: KeyWords) -> list[File]:
        """Get all files that have all of the required keywords"""
        keyword_filter = SstFileFilter(require_all=set(keywords))
        return keyword_filter(self.all)


if TYPE_CHECKING:
    _instance_check: FileFilter = SstFileFilter()
    _class_check: type[FileFilter] = SstFileFilter
    #
    _instance_check: FileFiltering = FileFilterMixin()
    _class_check: type[FileFiltering] = FileFilterMixin
