"""
Inspect arbitrary objects and safely pull out specific attributes

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "find",
    "doc",
    "name",
    "text",
    "module",
]


from collections.abc import Sequence
from typing import Any

from ...port.empty import VOID as _VOID


def find(target: Any, attrs: Sequence[str], default=None, /) -> Any:
    for attr in attrs:
        if (detected := getattr(target, attr, _VOID)) is not _VOID:
            return detected
    else:
        return default


def doc(target: Any, /, default="") -> str:
    """Extract __doc__ or default to empty string"""
    return find(target, ("__doc__",), default)


def module(target: Any, /, default: str = "NoModule") -> str:
    """Extract __module__ from functions, classes, or instances"""
    if module_name := find(target, ("__module__",)):
        return module_name
    return find(type(target), ("__module__",), default)


def name(target: Any, /, attrs: list[str] | None = None, default=" 󰂒 ") -> str:
    # LATER: extend with pre/post fix, eg: BaseName or NameDefault etc.
    """Check attribute list, provide match or default"""
    default_checks: list[str] = ["_inside_brackets", "_name", "name"]
    check_attrs: list[str] = (attrs or []) + default_checks
    return find(target, check_attrs, default)


def text(target: Any, /, attrs: list[str] | None = None) -> str | None:
    """Check if text in attribute list, provide match or None"""
    check_attrs: list[str] = (attrs or []) + ["_text", "text"]
    return find(target, check_attrs)
