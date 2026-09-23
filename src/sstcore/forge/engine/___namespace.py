"""
Funcions to Assemble NameSpace for Classes

                                                 DependencyLevel[0]
"""


def _rebase(cls: type, base: type) -> type:
    ns = {
        k: v
        for k, v in cls.__dict__.items()
        if k not in {"__dict__", "__weakref__"}
    }
    ns["__module__"] = cls.__module__
    ns["__qualname__"] = getattr(cls, "__qualname__", cls.__name__)
    ns["__annotations__"] = dict(getattr(cls, "__annotations__", {}))
    return type(cls.__name__, (base,), ns)
