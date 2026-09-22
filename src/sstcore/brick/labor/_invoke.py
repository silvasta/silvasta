"""
Invoke - Call the method on the Target

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "invoking",
    "rich",
    "cli",
    "log",
]

from collections.abc import Callable
from typing import Any


def invoking(_target: Any, /, method: str, *, strict: bool = False) -> Any:
    """Extract and execute specific method if it exists"""
    return __core__(_target, method, strict=strict)  # LATER: parametrize?


def __core__(  # noqa:N807
    _target: Any, /, method: str, *, strict: bool = False, default=None
) -> Any:  # LATER: use __core__ for sstcore.forge.blueprint|func
    try:
        extracted: Callable = getattr(_target, method)
        return extracted()
    except Exception as error:
        if strict:
            message = f"Invoking {_target}.{method} failed: {error}"
            raise AttributeError(message) from error
    return default


def _represent(_target: Any, /, method: str, *, strict: bool) -> Any:
    """Provide invoked value or default to str(target)"""
    return __core__(
        _target, method=method, strict=strict, default=str(_target)
    )


def rich(_target: Any, *, strict: bool = False) -> Any:
    """Provide __rich__ value or default to str(target)"""
    return _represent(_target, method="__rich__", strict=strict)


def cli(_target: Any, *, strict: bool = False) -> Any:
    # LATER: dispatch strict=True->CliDTO
    """Provide __cli__ value or default to str(target)"""
    return _represent(_target, method="__cli__", strict=strict)


def log(_target: Any, *, strict: bool = False) -> Any:
    # LATER: dispatch strict=True->LogDTO
    """Provide __log__ value or default to str(target)"""
    return _represent(_target, method="__log__", strict=strict)
