"""
...

                                                           ModuleLevel[0]
"""

__all__: list[str] = [
    "invoke",
    "rich",
    "cli",
    "log",
]

from typing import Any


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
