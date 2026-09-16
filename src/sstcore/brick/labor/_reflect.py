"""
Inspect arbitrary objects and safely pull out specific attributes

                                                           ModuleLevel[0]
"""

__all__: list[str] = [
    "clsname",
    "data",
    "pydantic",
    "just_return",
    # find
    "name",
    "text",
    # extract
    "invoke",
    "rich",
    "cli",
    "log",
]

# TASK: proper assembly and selection
# - group better by topic!

# STRATEGY: Catalog->Functor->Rule

from collections.abc import Callable
from typing import Any

from ...port.calling import PydanticModel


def clsname(_target: Any) -> str:
    """Extract name from instance or class"""
    return getattr(_target, "__name__", type(_target).__name__)


def just_return[Target](constant: Target) -> Callable[..., Target]:
    """Wrap _target in function that returns constant value"""

    def constant_function(*_, **__) -> Target:
        return constant

    return constant_function  # MOVE: to sstcore.brick.format|func


def data(_target: Any, exclude: set[str] | None = None) -> dict[str, Any]:
    """Extract public attributes filtered by exclude"""
    return {
        k: v
        for k, v in vars(_target).items()
        if not k.startswith("_") and k not in (exclude or set())
    }


def pydatic(
    _target: Any, *, exclude: set[str] | None = None
) -> dict[str, Any]:
    """Extract public Pydantic attributes filtered by exclude"""

    exclude: set[str] = exclude or set()

    if isinstance(_target, PydanticModel):
        return _target.model_dump(exclude=exclude)

    return data(_target, exclude)


def _dict(_target: Any, *, key: str) -> Any:
    """Direct __dict__ access"""
    return _target.__dict__[key]


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Find Attr
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

# TASK: later on all of this assembled to Functor
# - preinstalled with proper name and loggging
# - ready for like any task selected from catalog


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


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Invoke
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def invoke(_target: Any, method_name: str, *, strict: bool = False) -> Any:
    """Extract and execute specific method if it exists"""
    try:
        if method := getattr(_target, method_name, None):
            return method()
    except Exception as error:
        if strict:
            raise AttributeError(
                f"Issue for {_target} while extracting {method_name}: {error}"
            ) from error

    return str(_target)


def rich(_target: Any, *, strict: bool = False) -> Any:
    """Provide __rich__ value or default to str()"""
    return invoke(_target, method_name="__rich__", strict=strict)


def cli(_target: Any, *, strict: bool = False) -> Any:
    """Provide __cli__ value or default to str()"""
    return invoke(_target, method_name="__cli__", strict=strict)


def log(_target: Any, *, strict: bool = False) -> Any:
    """Provide __log__ value or default to str()"""
    return invoke(_target, method_name="__log__", strict=strict)
