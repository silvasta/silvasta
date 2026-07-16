"""
sstcore.utils — Generalize recurring patterns in projects.

Provide stable, low-level building blocks for this and other projects:

- Path management and guarding (sstcore.utils.path)
- Filtering and selection logic (sstcore.utils.filter)
- Log configuration (sstcore.utils.log)
- Rich-based printing and styling (sstcore.utils.print, sstcore.utils.color)
- Scanning and tree construction (sstcore.utils.scanner, sstcore.utils.tree)

Built on top of these major external dependencies:
- rich
- loguru

"""

__all__: list = [
    "printer",
    "PrinterFactory",
    "ColorBox",
    "FilterSet",
    "PathFilter",
    "ProjectFilter",
    "FolderScanner",
    "SimpleTreeNode",
    "PathTreeNode",
    "day_count",
    "PathGuard",
]


from .color import ColorBox
from .filter import FilterSet, PathFilter, ProjectFilter
from .path import PathGuard
from .print import PrinterFactory, printer
from .scanner import FolderScanner
from .time import day_count
from .tree import PathTreeNode, SimpleTreeNode
