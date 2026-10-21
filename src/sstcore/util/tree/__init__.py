"""
Build Tree-like structures - Directed Graphs

- Nodes: not per definition acyclic, but most of behaviour will break otherwise
- example_trees: few implementations as examples or to test renderings

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "example_trees",
    #
    "SimpleTreeNode",
    #
    "PathTreeNode",
    "build_path_tree",
    #
    "AstNode",
]

from . import _show as example_trees
from ._ast import AstNode
from ._path import PathTreeNode, build_path_tree
from ._simple import SimpleTreeNode
