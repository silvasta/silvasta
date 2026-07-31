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


def name(self: Any, attrs: list[str] | None = None) -> str:
    """Check attribute list, provide match or default"""
    for guess in (attrs or []) + [
        "_inside_brackets",  # TODO:
        "_name",
        "name",
    ]:
        if name := getattr(self, guess, ""):
            return name
    return " 󰂒 "  # TODO:


def text(self: Any, attrs: list[str] | None = None) -> str | None:
    """Check if text in attribute list, provide match or None"""
    for guess in (attrs or []) + ["_text", "text"]:
        if name := getattr(self, guess, ""):
            return name
    return None


def data(self: Any, exclude: set[str] | None = None) -> dict[str, Any]:
    """Extract public attributes filtered by exclude"""
    return {
        k: v
        for k, v in vars(self).items()
        if not k.startswith("_") and k not in (exclude or set())
    }


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
