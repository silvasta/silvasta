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
    "iter_submodules",
]

import importlib.util
import pkgutil
from collections.abc import Callable, Iterator
from importlib.machinery import ModuleSpec as _PyModuleSpec
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


def importing(target: Any, /, package: str | None = None) -> Any:
    """Validate target and import the module or qualname attribute."""
    modulepath: ModulePath = ModuleSpec.ok(target, allow_relative=bool(package))
    return modulepath.importing(package)


def iter_submodules(
    target: Any, /, *, include_private: bool = True
) -> Iterator[ModulePath]:
    """Yield ModulePaths for all Target submodules without importing them"""
    basemodule: ModulePath = ModuleSpec.ok(target, resolve=True)
    package: Path = package_dir(basemodule)
    for info in pkgutil.iter_modules([str(package)]):
        if include_private or not info.name.startswith("_"):
            yield basemodule / info.name


def lazy_loader[R](
    target: Any,
    /,
    *,
    call_if_callable: bool = True,
    ensure_exists: bool = False,
    package: str | None = None,
) -> Callable[[], R]:
    """Validate target and bind a zero-arg lazy import closure."""
    modulepath: ModulePath = ModuleSpec.ok(target, allow_relative=bool(package))
    return modulepath.lazy_loader(
        call_if_callable=call_if_callable,
        ensure_exists=ensure_exists,
        package=package,
    )


def module_root(obj: Any, package: str | None = None, /) -> Path:
    """Resolve the filesystem directory of an object's nearest public package"""
    if isinstance(obj, Path) and package is None:
        return package_dir(obj)
    return package_dir(package or public_package(obj))


def package_dir(target: Any, /) -> Path:
    """Resolve module/package (or object) to its filesystem directory"""

    if isinstance(target, Path):
        resolved: Path = target.resolve()
        return resolved if resolved.is_dir() else resolved.parent

    spec: _PyModuleSpec = _find_spec(target)

    return _search_dir(spec) or _origin_file(spec).parent


def module_file(target: Any) -> Path:
    """Resolve a module or object to its exact .py source file on disk."""

    if isinstance(target, Path) and target.is_file():
        return target.resolve()

    spec: _PyModuleSpec = _find_spec(target)

    return _origin_file(spec)


#  LINE: -- Helper -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _find_spec(target: Any, /) -> _PyModuleSpec:
    """Step 1: Normalize target to absolute ModulePath and locate its Python ModuleSpec."""
    mp: ModulePath = ModuleSpec.ok(target, resolve=True)
    if (spec := importlib.util.find_spec(mp.module)) is None:
        raise ModuleNotFoundError(f"Missing module: {mp.module!r}")
    return spec


def _search_dir(spec: _PyModuleSpec, /) -> Path | None:
    """Step 2a: Extract package directory from submodule_search_locations if present."""
    if locs := spec.submodule_search_locations:
        return Path(next(iter(locs))).resolve()
    return None


def _origin_file(spec: _PyModuleSpec, /) -> Path:
    """Step 2b: Extract and validate concrete disk source file from spec.origin."""
    if not (origin := spec.origin) or origin in {"built-in", "frozen"}:
        raise ValueError(f"Module has no disk source file: {spec.name!r}")
    return Path(origin).resolve()
