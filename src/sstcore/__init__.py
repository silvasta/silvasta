"""
AUTO-GENARATED

- DO NOT EDIT!

"""

from importlib import import_module
from importlib.metadata import PackageNotFoundError, version

_LAZY_IMPORTS = {
    "SafeTyper": ".console",
    "System": ".system",
    "ConfigManager": ".system.config",
    "Emitter": ".system.event",
    "PathGuard": ".util.path.guard",
    "printer": ".util.print",
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        module_path = _LAZY_IMPORTS[name]
        module = import_module(module_path, package=__package__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return list(_LAZY_IMPORTS.keys())


try:
    __version__: str = version(distribution_name="sstcore-py")
    # AI: fixed from sstcore, must be like toml right? not like package in src
except PackageNotFoundError:
    __version__ = "unknown"
