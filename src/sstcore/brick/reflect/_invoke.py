"""
Invoke - Call the method on the Target

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "rich",
    "cli",
    "log",
]

from collections.abc import Callable
from typing import Any


def _invoke(
    target: Any, /, method: str, default=None, *, strict: bool = False
) -> Any:
    """Extract and execute specific method if it exists"""
    return __core__(
        target, method, default, strict=strict
    )  # LATER: parametrize?


def __core__(  # noqa:N807
    target: Any, /, method: str, default=None, *, strict: bool = False
) -> Any:  # LATER: use __core__ for sstcore.forge.blueprint|func
    try:
        extracted: Callable = getattr(target, method)
        return extracted()
    except Exception as error:
        if strict:
            message = f"Invoking {target}.{method} failed: {error}"
            raise AttributeError(message) from error
    return default


def _represent(target: Any, /, method: str, *, strict: bool) -> Any:
    """Provide invoked value or default to str(target)"""
    return __core__(target, method=method, default=str(target), strict=strict)


def rich(target: Any, /, *, strict: bool = False) -> Any:
    """Provide __rich__ value or default to str(target)"""
    return _represent(target, method="__rich__", strict=strict)


def cli(target: Any, /, *, strict: bool = False) -> Any:
    # LATER: dispatch strict=True->CliDTO
    """Provide __cli__ value or default to str(target)"""
    return _represent(target, method="__cli__", strict=strict)


def log(target: Any, /, *, strict: bool = False) -> Any:
    # LATER: dispatch strict=True->LogDTO
    """Provide __log__ value or default to str(target)"""
    return _represent(target, method="__log__", strict=strict)
