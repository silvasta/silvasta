"""
Find and Match Package- and Module- with FileSystem Paths

                           DependencyLevel.sstcore.util.path[4.X.1]
"""

__all__: list[str] = [
    "module_name",
    "public_package",
    "module_root",
    "package_dir",
    "module_file",
]


import importlib.util
from pathlib import Path
from typing import Any

from ...port.structures._module import ModulePath
from ._modulecast import ModuleSpec


def module_name(obj: Any, /) -> str:
    """Extract canonical module name from any object or string"""
    return ModuleSpec.ok(obj, allow_relative=True).module


def public_package(target: Any, /) -> str:
    """Walk upwards until next public package"""
    return ModuleSpec.ok(target).public


def module_root(obj: Any, package: str | None = None, /) -> Path:
    """Resolve the filesystem directory of an object's nearest public package"""
    return package_dir(package or public_package(obj))


def package_dir(target: Any, /) -> Path:
    """Resolve module/package (or object) to its filesystem directory"""

    mp: ModulePath = ModuleSpec.ok(target, resolve=True)

    # TASK: compare with module_file
    if (spec := importlib.util.find_spec(mp.module)) is None:
        raise ModuleNotFoundError(f"Missing module: {mp.module!r}")

    if spec.submodule_search_locations:
        return Path(next(iter(spec.submodule_search_locations))).resolve()

    if not spec.origin or spec.origin in {"built-in", "frozen"}:
        raise ValueError(f"Not found on disk: {mp.module!r}")

    return Path(spec.origin).resolve().parent


def module_file(target: Any) -> Path:
    """Resolve a module or object to its exact .py source file on disk."""

    mp: ModulePath = ModuleSpec.ok(target, resolve=True)

    # TASK: compare with package_dir, unify errors, remove duplication
    if (spec := importlib.util.find_spec(mp.module)) is None or not spec.origin:
        raise ModuleNotFoundError(
            f"Cannot locate source file for: {mp.module!r}"
        )
    if spec.origin in {"built-in", "frozen"}:
        raise ValueError(
            f"Built-in/frozen module has no disk file: {mp.module!r}"
        )
    return Path(spec.origin).resolve()
