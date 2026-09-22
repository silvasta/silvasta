"""
Inspect arbitrary objects and safely pull out specific attributes

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "clsname",
    "funcname",
    #
    "reflecting",
    "doc",
    "name",
    "text",
]


from collections.abc import Sequence
from typing import Any, overload


def clsname(_target: Any, default="") -> str:
    """Extract name from instance or class"""
    default: str = default or type(_target).__name__
    return __core__(_target, attrs=("__name__",), default=default)


def funcname(_target: Any, default="Func") -> str:
    """Check attribute list, provide match or default"""
    attrs: Sequence[str] = ("__name__", "__qualname__")
    return __core__(_target, attrs, default)


@overload
def reflecting[T](_target: Any, attrs: Sequence[str]) -> Any: ...
@overload
def reflecting[T](_target: Any, attrs: Sequence[str], default: T) -> T: ...  #
def reflecting[T](
    _target: Any, attrs: Sequence[str], default: T | None = None
) -> Any:
    """Work trough attrs with getattr and provide first hit or default"""
    return __core__(_target, attrs, default)


def __core__(_target: Any, attrs: Sequence[str], default=None) -> Any:  # noqa:N807
    # LATER: use __core__ for sstcore.forge.blueprint|func
    for guess in attrs:
        if detected := getattr(_target, guess, None):
            return detected
    else:
        return default


def doc(_target: Any, /, default="") -> str:
    """Extract __doc__ or default to empty string"""
    return __core__(_target, ("__doc__",), default=default)


def name(_target: Any, attrs: list[str] | None = None, default=" 󰂒 ") -> str:
    # LATER: extend with pre/post fix, eg: BaseName or NameDefault etc.
    """Check attribute list, provide match or default"""
    default_checks: list[str] = ["_inside_brackets", "_name", "name"]
    check_attrs: list[str] = (attrs or []) + default_checks
    return __core__(_target, check_attrs, default)


def text(_target: Any, attrs: list[str] | None = None) -> str | None:
    """Check if text in attribute list, provide match or None"""
    check_attrs: list[str] = (attrs or []) + ["_text", "text"]
    return __core__(_target, check_attrs)
