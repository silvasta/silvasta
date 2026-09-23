"""
Funcions to Assemble NameSpace for Classes

                            DependencyLevel.sstcore.forge.engine[0]
"""

from typing import Any

type NameSpace = dict[str, Any]


def rebase(cls: type, base: type) -> type:
    ns: NameSpace = {
        k: v
        for k, v in cls.__dict__.items()
        if k not in {"__dict__", "__weakref__"}
    }  # EXTRACT:
    ns["__module__"] = cls.__module__
    ns["__qualname__"] = getattr(cls, "__qualname__", cls.__name__)
    ns["__annotations__"] = dict(getattr(cls, "__annotations__", {}))
    return type(cls.__name__, (base,), ns)
