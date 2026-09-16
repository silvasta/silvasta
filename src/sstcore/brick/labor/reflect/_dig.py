"""
Dig into the Target and find Attrs

                                                           ModuleLevel[0]
"""

__all__: list[str] = [
    "dig",
    "name",
    "text",
    "func",
]

from typing import Any


def dig(_target: Any, attrs: list[str], default=None) -> Any | None:
    """Work trough the list with getattr and provide first hit or default"""

    for guess in attrs:
        if detected := getattr(_target, guess, ""):
            return detected
    else:
        return default


def name(_target: Any, attrs: list[str] | None = None, default=" 󰂒 ") -> str:
    # LATER: extend with pre/post fix, eg: BaseName or NameDefault etc.
    """Check attribute list, provide match or default"""
    default_checks: list[str] = ["_inside_brackets", "_name", "name"]
    check_attrs: list[str] = (attrs or []) + default_checks
    if detected := dig(_target, check_attrs):
        return detected
    return default


def text(_target: Any, attrs: list[str] | None = None) -> str | None:
    """Check if text in attribute list, provide match or None"""
    check_attrs: list[str] = (attrs or []) + ["_text", "text"]
    return dig(_target, check_attrs)


def func(_target: Any, attrs: list[str] | None = None, default="Func") -> str:
    """Check attribute list, provide match or default"""
    default_checks: list[str] = ["__qualname__", "__name__"]
    check_attrs: list[str] = (attrs or []) + default_checks
    if detected := dig(_target, check_attrs):
        return detected
    return default
