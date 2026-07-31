"""
Filter - Stacked in different combinations.

FilterArgs: Base DTO with all sets
FilterSet: Core logic with all checks
PathFilter: Decompose Paths for target set
ProjectFilter: For directories with code

Others:
  - SstFileFilter (assembled in data due to dependency)

                                                       DependencyLevel[X]
"""

__all__: list[str] = [
    "FilterArgs",
    "FilterSet",
    "FilterBox",
    "PathFilter",
    "ProjectFilter",
]
from ._box import FilterBox
from ._path import PathFilter, ProjectFilter
from ._set import FilterArgs, FilterSet
