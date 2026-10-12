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


def clsname(target: Any, /, default="") -> str:
    """Extract name from instance or class"""
    default: str = default or type(target).__name__
    return __core__(target, attrs=("__name__",), default=default)


def funcname(target: Any, /, default="Func") -> str:
    """Check attribute list, provide match or default"""
    attrs: Sequence[str] = ("__name__", "__qualname__")
    return __core__(target, attrs, default)


@overload
def reflecting[T](target: Any, /, attrs: Sequence[str]) -> Any: ...
@overload
def reflecting[T](
    target: Any, /, attrs: Sequence[str], default: T
) -> T: ...  #
def reflecting[T](
    target: Any, /, attrs: Sequence[str], default: T | None = None
) -> Any:
    """Work trough attrs with getattr and provide first hit or default"""
    return __core__(target, attrs, default)


def __core__(target: Any, /, attrs: Sequence[str], default=None) -> Any:  # noqa:N807
    # LATER: use __core__ for sstcore.forge.blueprint|func
    for attr in attrs:
        if detected := getattr(target, attr, None):
            return detected
    else:
        return default


def doc(target: Any, /, default="") -> str:
    """Extract __doc__ or default to empty string"""
    return __core__(target, ("__doc__",), default=default)


def name(target: Any, /, attrs: list[str] | None = None, default=" 󰂒 ") -> str:
    # LATER: extend with pre/post fix, eg: BaseName or NameDefault etc.
    """Check attribute list, provide match or default"""
    default_checks: list[str] = ["_inside_brackets", "_name", "name"]
    check_attrs: list[str] = (attrs or []) + default_checks
    return __core__(target, check_attrs, default)


def text(target: Any, /, attrs: list[str] | None = None) -> str | None:
    """Check if text in attribute list, provide match or None"""
    check_attrs: list[str] = (attrs or []) + ["_text", "text"]
    return __core__(target, check_attrs)
