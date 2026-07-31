"""
Handle basic File System Operations, find and extract from Paths

                                                       DependencyLevel[X]
"""

__all__: list[str] = [
    # search
    "recursive_root",
    "recursive_parent",
    "any_root",
    "find_project_root",
    "get_project_root",
    # pyproject.toml
    "pytoml",
    "pyproject_path",
    "pyproject_name",
    "pyproject_sns",
]

from . import _toml as pytoml
from ._search import (
    any_root,
    find_project_root,
    get_project_root,
    recursive_parent,
    recursive_root,
)
from ._toml import pyproject_name, pyproject_path, pyproject_sns
