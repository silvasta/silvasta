"""
sstcore - Generalize Project Patterns and Bootstrap with Batteries
"""

from typing import TYPE_CHECKING

__all__: list[str] = [
    "SafeTyper",
    "ConfigManager",
    "System",
]

# 1. Type Checkers see this. Runtime ignores it.
if TYPE_CHECKING:
    from .cli import SafeTyper
    from .config import ConfigManager
    from .system import System

# 2. Runtime uses this. Type Checkers ignore it.
_LAZY_MAP = {
    "SafeTyper": ".cli",
    "ConfigManager": ".config",
    "System": ".system",
}


def __getattr__(name: str):
    if name in _LAZY_MAP:
        import importlib

        module = importlib.import_module(_LAZY_MAP[name], package=__name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return __all__
