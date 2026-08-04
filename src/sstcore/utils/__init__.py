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

                                                       DependencyLevel[3]
"""

__all__: list = [
    "FolderScanner",
    "PathGuard",
    "Printer",
    "PrinterFactory",
    "printer",
    "SchemaName",
    "SimpleTreeNode",
    "day_count",
    "view",
]


from .parse import SchemaName
from .path.guard import PathGuard
from .print import Printer, PrinterFactory, printer
from .scanner import FolderScanner
from .time import day_count
from .tree import SimpleTreeNode
from .view import view
