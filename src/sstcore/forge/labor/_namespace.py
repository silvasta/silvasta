"""
Functions to Assemble NameSpace for Classes

                            DependencyLevel.sstcore.forge.engine[0]
"""

from typing import Any

type NameSpace = dict[str, Any]

SKIP: set[str] = {"__dict__", "__weakref__"}


def copy_namespace(cls: type, skip: set[str] = SKIP) -> dict[str, object]:
    """Extract Class NameSpace for a new Base (Builder/Meta)"""

    ns: NameSpace = {k: v for k, v in cls.__dict__.items() if k not in skip}

    ns["__module__"] = cls.__module__
    ns["__qualname__"] = getattr(cls, "__qualname__", cls.__name__)
    ns["__annotations__"] = dict(getattr(cls, "__annotations__", {}))

    return ns


def rebase(cls: type, base: type, skip=SKIP) -> type:
    """Copy Class NameSpace onto a new Base (Builder/Meta)"""

    return type(cls.__name__, (base,), copy_namespace(cls, skip))
