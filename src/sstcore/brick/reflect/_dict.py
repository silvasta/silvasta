"""
Directly operate at the targets 'Heart'

- Inspect (and modify?) object.__dict__

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "full",
]


import sys
from types import ModuleType
from typing import Any

# NEXT: check port.link._operator


class CallableDictModule(ModuleType):
    def __call__(self, target: Any, key: str, /):
        """Direct __dict__ access"""
        return target.__dict__[key]


def full(target, /) -> list[Any]:
    self: Any = None  # FIX:
    return [
        CallableDictModule.__call__(self, target, key)
        for key in target.__dict__.items()
    ]


sys.modules[__name__].__class__ = CallableDictModule
