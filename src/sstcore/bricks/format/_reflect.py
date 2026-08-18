"""
Inspect arbitrary objects and safely pull out specific attributes

                                                           ModuleLevel[0]
"""

__all__: list[str] = [
    "cls_name",
    "name",
    "text",
    "data",
    #
    "invoke",
    "rich",
    "cli",
    "log",
]

from typing import Any


def cls_name(target: Any) -> str:
    """Safely extract class name from instances or classes."""
    return getattr(target, "__name__", type(target).__name__)


def data(target: Any, exclude: set[str] | None = None) -> dict[str, Any]:
    """Extract public attributes filtered by exclude"""
    return {
        k: v
        for k, v in vars(target).items()
        if not k.startswith("_") and k not in (exclude or set())
    }


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Find Attr
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def dig_attr(target: Any, check_attrs: list[str], default=None) -> str | None:
    for guess in check_attrs:
        if detected := getattr(target, guess, ""):
            return detected
    else:
        return default


def name(target: Any, attrs: list[str] | None = None, default=" 󰂒 ") -> str:
    """Check attribute list, provide match or default"""
    default_checks: list[str] = ["_inside_brackets", "_name", "name"]
    check_attrs: list[str] = (attrs or []) + default_checks
    if detected := dig_attr(target, check_attrs):
        return detected
    return default


def text(target: Any, attrs: list[str] | None = None) -> str | None:
    """Check if text in attribute list, provide match or None"""
    check_attrs: list[str] = (attrs or []) + ["_text", "text"]
    return dig_attr(target, check_attrs)


def func(target: Any, attrs: list[str] | None = None, default="Func") -> str:
    """Check attribute list, provide match or default"""
    default_checks: list[str] = ["__qualname__", "__name__"]
    check_attrs: list[str] = (attrs or []) + default_checks
    if detected := dig_attr(target, check_attrs):
        return detected
    return default


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Invoke
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def invoke(target: Any, method_name: str, *, strict: bool = False) -> Any:
    """Extract and execute specific method if it exists"""
    try:
        if method := getattr(target, method_name, None):
            return method()
    except Exception as error:
        if strict:
            raise AttributeError(
                f"Issue for {target} while extracting {method_name}: {error}"
            ) from error

    return str(target)


def rich(target: Any, *, strict: bool = False) -> Any:
    """Provide __rich__ value or default to str()"""
    return invoke(target, method_name="__rich__", strict=strict)


def cli(target: Any, *, strict: bool = False) -> Any:
    """Provide __cli__ value or default to str()"""
    return invoke(target, method_name="__cli__", strict=strict)


def log(target: Any, *, strict: bool = False) -> Any:
    """Provide __log__ value or default to str()"""
    return invoke(target, method_name="__log__", strict=strict)
