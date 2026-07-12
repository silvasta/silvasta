"""
sstcore.utils — Generalize recurring patterns in projects.

Provide stable, low-level building blocks for this and other projects:

- Path management and guarding (sstcore.utils.path)
- Filtering and selection logic (sstcore.utils.filter)
- Log configuration (sstcore.utils.log)
- Rich-based printing and styling (sstcore.utils.print, sstcore.utils.color)
- Scanning and tree construction (sstcore.utils.scanner, sstcore.utils.tree)
- Time utilities (sstcore.utils.time)

Built on top of these major external dependencies:
- rich
- loguru

"""

__all__: list = [
    "day_count",
    "HomeSetup",
    "XdgHomes",
    "PathGuard",
    "printer",
    "Printer",
    "create_printer",
    "setup_logging",
    "FilterSet",
    "PathFilter",
    "ProjectFilter",
    "FolderScanner",
    "SimpleTreeNode",
    "PathTreeNode",
    "NamePattern",
    "ColorBox",
]


from .color import ColorBox
from .filter import FilterSet, PathFilter, ProjectFilter
from .log import setup_logging
from .parse import NamePattern
from .path import HomeSetup, PathGuard, XdgHomes
from .print import Printer, create_printer, printer
from .scanner import FolderScanner
from .time import day_count
from .tree import PathTreeNode, SimpleTreeNode
