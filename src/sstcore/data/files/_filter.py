"""
Provide Container for Files and Tools for FileSystem Operations

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "FileFilterMixin",
]


from typing import TYPE_CHECKING

from ...brick.registry import ListRegistry
from ...port.files import File, FileFiltering
from ...util.filter import FileFilter

type KeyWords = str | list[str] | set[str]


class FileFilterMixin(ListRegistry[File]):
    """Provide Keyword filtering"""

    filter: FileFiltering = FileFilter()  # TODO: better...

    def set_filter(self, file_filter: FileFilter) -> None:
        """Install new custom FileFilter"""
        self.filter: FileFilter = file_filter

    # NEXT:
    # def get_by_filter(
    #     self, file_filter: FileFilter | None = None
    # ) -> list[File]:
    #     """Get all files filtered by keywords setup in file_filter"""
    #     return self.filter(file_filter)

    def get_by_keyword(self, keywords: KeyWords) -> list[File]:
        """Get all files that have at least 1 of the required keywords"""
        keyword_filter = FileFilter(require_any=set(keywords))
        return keyword_filter(list(self.all))

    def get_by_all_keywords(self, keywords: KeyWords) -> list[File]:
        """Get all files that have all of the required keywords"""
        keyword_filter = FileFilter(require_all=set(keywords))
        return keyword_filter(list(self.all))


if TYPE_CHECKING:
    _instance_check: FileFilter = SstFileFilter()
    _class_check: type[FileFilter] = SstFileFilter
    #
    _instance_check: FileFiltering = FileFilterMixin()
    _class_check: type[FileFiltering] = FileFilterMixin
