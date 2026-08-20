"""
Filter - Stacked in different combinations.

- FilterSet: Core logic with all checks
- FilterData: Base DTO with all sets
- FilterArgs: Select from Filter input presets

- PathFilter: Decompose Paths for target set
- ProjectFilter: For directories with code
                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "FilterSet",
    "FilterData",
    "FilterArgs",
    #
    "FileFilter",
    "PathFilter",
    "ProjectFilter",
]
from ._base import FilterData
from ._box import FilterArgs
from ._core import FilterSet
from ._filters import FileFilter, PathFilter, ProjectFilter
