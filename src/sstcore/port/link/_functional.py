"""
Execution Primitives

                               DependencyLevel.sstcore.port.link[0]
"""

# IMPORTANT: who is using this? maybe just _control -> move to _control

from collections.abc import Callable, Sequence
from typing import Any

INIT = ("__post_init__", "__init__")


def _unpack(  # MOVE: closer to Tap?
    func: Callable[..., Any], qual: str, is_method: bool, args: tuple[Any, ...]
) -> tuple[str, Sequence[Any]]:
    """Resolve dynamic method sender and unbound args in one step."""

    if is_method and args:
        target, *unbound = args
        return f"{_who(target)}.{func.__name__}", unbound  # ty:ignore

    return qual, args


def _dict_hits(cls: type, *attrs: str, init: bool = False) -> list[Callable]:
    """Extract matching callables if present directly from cls.__dict__"""

    methods: list = [cls.__dict__[a] for a in attrs if a in cls.__dict__]

    if init and (_init_ := _dict_hits(cls, *INIT, init=False)):
        methods.append(_init_[0])  # prefers __post_init__ if exists

    return methods


def _qual(target: Any, /) -> str:  # RENAME: qualname? but module..? keyname?
    """Generate full module.qualname path for scope matching"""
    module: str = getattr(target, "__module__", "")
    # NOTE: Detector primitives?
    qualname: str = getattr(
        target, "__qualname__", getattr(type(target), "__qualname__", "")
    )
    return f"{module}.{qualname}"  # CHECK: ".qualname"?


def _who(target: Any, /) -> str:
    """Format a readable sender label for instances, classes, or strings."""
    if target is None:
        return ""  # IDEA: raise? but such that i easy to capture and continue
    if isinstance(target, str):
        return target
    if isinstance(target, type):
        return target.__name__
    return str(target)
