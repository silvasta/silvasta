"""
Build Tree-like structures - Directed Graphs

- Nodes: not per definition acyclic, but most of behaviour will break otherwise
- example_trees: few implementations as examples or to test renderings

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "SimpleTreeNode",
    "PathTreeNode",
    "build_path_tree",
    "example_trees",
]

from . import _examples as example_trees
from ._nodes import PathTreeNode, SimpleTreeNode, build_path_tree
