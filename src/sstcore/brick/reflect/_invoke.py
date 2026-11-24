"""
Invoke - Call the method on the Target

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "call",
    "rich",
    "cli",
    "log",
]

from collections.abc import Callable as _Callable
from typing import Any as _Any


def call(
    target: _Any,
    method: str,
    default=None,
    /,
    *,
    strict: bool = False,
) -> _Any:
    try:
        extracted: _Callable = getattr(target, method)
        return extracted()
    except Exception as error:
        if strict:
            message = f"Invoking {target}.{method} failed: {error}"
            raise AttributeError(message) from error
    return default


def _represent(target: _Any, method: str, /, *, strict: bool) -> _Any:
    """Provide invoked value or default to str(target)"""
    return call(target, method, str(target), strict=strict)


def rich(target: _Any, /, *, strict: bool = False) -> _Any:
    """Provide __rich__ value or default to str(target)"""
    return _represent(target, "__rich__", strict=strict)


def cli(target: _Any, /, *, strict: bool = False) -> _Any:
    # LATER: dispatch strict=True->CliDTO
    """Provide __cli__ value or default to str(target)"""
    return _represent(target, "__cli__", strict=strict)


def log(target: _Any, /, *, strict: bool = False) -> _Any:
    # LATER: dispatch strict=True->LogDTO
    """Provide __log__ value or default to str(target)"""
    return _represent(target, "__log__", strict=strict)
