"""
Filter - Stacked in different combinations.

- FilterSet: Core logic with dispatches and checks
- FilterData: Base DTO with sets and manipulation
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
from ._engine import FilterSet
from ._filters import FileFilter, PathFilter, ProjectFilter
