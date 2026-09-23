"""
Find and Match Package- and Module- with FileSystem Paths

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    # "",
]

import importlib.util
import inspect
from collections.abc import Callable
from importlib import resources
from pathlib import Path
from types import ModuleType
from typing import Any


def get_package_root(package_name: str) -> Path:
    # Возвращает Path к папке пакета (не к __init__.py, а к директории)
    return resources.files(package_name).parent


# EXTRACT:
root = get_package_root("sstcore.brick.stack")
stub_path = root / "__init__.pyi"


def ppackage_dir(pkg_name: str) -> Path:
    spec = importlib.util.find_spec(pkg_name)
    if spec is None or spec.origin is None:
        raise ValueError(
            f"Package {pkg_name} not found or not a real file-based package"
        )
    # spec.origin — это путь к __init__.py
    return Path(spec.origin).parent


def resolve_stub_dir(
    target: str | ModuleType | Path, subdir: str = "_stubs"
) -> Path:
    """Stable resolution of where stubs should live."""
    if isinstance(target, Path):
        pkg_dir = target
    elif isinstance(target, str):
        mod = importlib.import_module(
            target if "." in target else f"sstcore.{target}"
        )
        pkg_dir = Path(inspect.getfile(mod)).parent
    else:
        pkg_dir = Path(inspect.getfile(target)).parent

    stub_dir = pkg_dir / subdir
    stub_dir.mkdir(parents=True, exist_ok=True)
    return stub_dir


#  LINE: -- g46 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def module_name_of(obj: Any) -> str:
    if inspect.ismodule(obj):
        return obj.__name__
    if inspect.isclass(obj) or inspect.isfunction(obj):
        return obj.__module__
    call = getattr(obj, "call", None)
    if isinstance(call, Callable) and getattr(call, "__module__", None):
        return call.__module__
    return type(obj).__module__


def public_package_name(module_name: str) -> str:
    """
    Amazing description, i hope the function is better...

    sstcore.brick.stack._example → sstcore.brick.stack
    sstcore.brick.color.____stack → sstcore.brick.color
    sstcore.brick.stack → sstcore.brick.stack
    """
    parts = module_name.split(".")
    while len(parts) > 1 and parts[-1].startswith("_"):
        parts.pop()
    return ".".join(parts)


def package_dir(dotted: str) -> Path:
    spec = importlib.util.find_spec(dotted)
    if spec is None:
        raise ModuleNotFoundError(dotted)
    if spec.submodule_search_locations:
        return Path(next(iter(spec.submodule_search_locations)))
    origin = spec.origin
    if not origin or origin in {"built-in", "frozen"}:
        raise ValueError(f"{dotted!r} has no file origin")
    path = Path(origin)
    return path.parent if path.name == "__init__.py" else path.parent


def project_root(anchor: str = "sstcore") -> Path:
    start = package_dir(anchor)
    for parent in (start, *start.parents):
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    raise FileNotFoundError("no project root above " + str(start))


def stub_paths(
    obj: Any, *, prefix: str, package: str | None = None
) -> tuple[Path, Path]:
    dotted = package or public_package_name(module_name_of(obj))
    root = package_dir(dotted)
    project = project_root()
    if not root.resolve().is_relative_to(project.resolve()):
        raise ValueError(f"{root} is not inside {project} (refusing to write)")
    stubs = root / "_stubs"
    return stubs / f"_{prefix.lower()}.pyi", root / "__init__.pyi"


def resolve_package_path(module_name: str) -> Path:
    """Safely resolve a dotted module name to its directory path."""
    spec = importlib.util.find_spec(module_name)
    if spec is None or spec.origin is None:
        raise ImportError(f"Cannot locate module: {module_name}")

    # spec.origin is the path to the __init__.py file
    return Path(spec.origin).parent


# Usage in your pipeline
target_dir = resolve_package_path("sstcore.brick.stack")
stub_file = target_dir / "__init__.pyi"
