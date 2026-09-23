"""
Find and Match Package- and Module- with FileSystem Paths

- ModuleName: "sstcore.brick.stack" -> is Dotted

                               DependencyLevel.sstcore.util.path[1]
"""

__all__: list[str] = [
    "package_dir",
    "module_name",
    "public_package",
    "get_stub_dir",
]

import importlib.util
import inspect
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any


def module_name(obj: Any) -> str:
    """Accepts modules, classes, functions, and callables"""

    if inspect.ismodule(obj):
        return obj.__name__

    if inspect.isclass(obj) or inspect.isfunction(obj):
        return obj.__module__

    call: Any | None = getattr(obj, "call", None)

    if isinstance(call, Callable) and getattr(call, "__module__", None):
        return call.__module__

    return type(obj).__module__


def public_package(module_name: str) -> str:
    """Walk upwards until next public Package"""

    parts: list[str] = module_name.split(".")

    while len(parts) > 1 and parts[-1].startswith("_"):
        parts.pop()

    return ".".join(parts)


def package_dir(dot_path: str) -> Path:
    """Resolve DotPath ModuleName to FileSystem Location or Raise"""

    if (spec := importlib.util.find_spec(dot_path)) is None:
        raise ModuleNotFoundError(f"Missind Module: {dot_path=}")

    if spec.submodule_search_locations:
        return Path(next(iter(spec.submodule_search_locations))).resolve()

    if not spec.origin or spec.origin in {"built-in", "frozen"}:
        raise ValueError(f"Not found on Disk: {dot_path!r}!")

    return Path(spec.origin).resolve().parent


def stub_root(obj: Any, package: str | None = None) -> Path:
    module: str = module_name(obj)
    dot_path: str = package or public_package(module_name=module)
    root: Path = package_dir(dot_path)
    return root


def get_stub_dir(
    target: str | ModuleType | Path, subdir: str = "_stubs"
) -> Path:  # LATER: target: DotPathSpec ?
    """Stable resolution of where stubs should live."""

    match target:
        case Path():
            base_dir: Path = target if target.is_dir() else target.parent
        case str():
            base_dir: Path = package_dir(target)
        case _:
            base_dir: Path = package_dir(module_name(target))

    path: Path = base_dir / subdir
    path.mkdir(parents=True, exist_ok=True)
    return path
