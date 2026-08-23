"""
Provide Container for Files and Tools for FileSystem Operations

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "FileFilterMixin",
]


from typing import TYPE_CHECKING

from ...brick.registry import FilterRegistry, ListRegistry
from ...port.files import File, FileFilterRegistry
from ...port.filter import Filter, KeyWords
from ...util.filter import FileFilter


class FileFilterMixin(FilterRegistry, ListRegistry[File]):  # LATER: emit?
    """Provide Keyword filtering"""

    def get_by_keyword(self, keywords: KeyWords) -> list[File]:
        """Get all files that have at least 1 of the required keywords"""
        keyword_filter = FileFilter(require_any=set(keywords))
        return keyword_filter(list(self.all))

    def get_by_all_keywords(self, keywords: KeyWords) -> list[File]:
        """Get all files that have all of the required keywords"""
        keyword_filter = FileFilter(require_all=set(keywords))
        return keyword_filter(list(self.all))


if TYPE_CHECKING:
    _instance_check: Filter = FileFilter()
    _class_check: type[Filter] = FileFilter
    #
    _instance_check: FileFilterRegistry = FileFilterMixin()
    _class_check: type[FileFilterRegistry] = FileFilterMixin
