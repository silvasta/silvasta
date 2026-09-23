"""
Handle basic File System Operations, find and extract from Paths

                                    DependencyLevel.sstcore.util[X]
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
    "ProjectInfo",
    "pyproject_path",
    "pyproject_name",
    "pyproject_sns",
    # homes
    "XdgDefaults",
    "XdgHomes",
    "HomeDirs",
    # modules
    "package_dir",
    "module_name",
    "public_package",
    "get_stub_dir",
]

from . import _toml as pytoml
from ._module import get_stub_dir, module_name, package_dir, public_package
from ._search import (
    any_root,
    find_project_root,
    get_project_root,
    recursive_parent,
    recursive_root,
)
from ._toml import (
    ProjectInfo,
    pyproject_name,
    pyproject_path,
    pyproject_sns,
)
from ._xdg import HomeDirs, XdgDefaults, XdgHomes
