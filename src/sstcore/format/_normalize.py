"""
Provide Base Level Text Formatting

- Normalize input for Modules without acces to sstcore.utils
                                                           ModuleLevel[0]
"""
# INFO: Intended as Package Root

__all__: list[str] = [
    "cls_name",
]

from typing import Any


def cls_name(target: Any) -> str:
    """Safely extract class name from instances or classes."""
    return getattr(target, "__name__", type(target).__name__)
