"""
Filter - Stacked in different combinations.

FilterSet: Base
PathFilter: Decompose and Filter
ProjectFilter: For Software Directories
PathFilter: Apply Schema and Pattern in regex Filter

"""

__all__: list[str] = [
    "FilterSet",
    "PathFilter",
    "PROJECT_IGNORE_DIRS",
    "PROJECT_ALLOWED_EXTS",
    "ProjectFilter",
    "PatternFilter",
]
from .path import (
    PROJECT_ALLOWED_EXTS,
    PROJECT_IGNORE_DIRS,
    PathFilter,
    PatternFilter,
    ProjectFilter,
)
from .set import FilterSet
