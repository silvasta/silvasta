"""
Provide Base Level string Formatting

- Normalize and Valide input for Modules without imports (from utils...)

                                                           ModuleLevel[0]
"""

__all__: list[str] = [
    "cls_name",
]

from typing import Any


def cls_name(target: Any) -> str:
    """Safely extract class name from instances or classes."""
    return getattr(target, "__name__", type(target).__name__)
