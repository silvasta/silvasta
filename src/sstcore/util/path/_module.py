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

from ._search import get_project_root
from .guard import PathGuard


def stub_paths(  # MOVE: to config.Paths, too much configuration here
    obj: Any, *, prefix: str, package: str | None = None
) -> tuple[Path, Path]:
    # EXTRACT: StubPath
    dot_path: str = package or public_package(module_name(obj))
    root: Path = package_dir(dot_path)
    project: Path = get_project_root()
    # LATER: apply PathGuard.relative
    if not root.resolve().is_relative_to(project.resolve()):
        raise ValueError(f"{root} is not inside {project} (refusing to write)")
    stubs = root / "_stubs"
    return stubs / f"_{prefix.lower()}.pyi", root / "__init__.pyi"


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# TODO: @PathGuard.Absorb
def package_dir(dot_path: str) -> Path:
    """Resolve DotPath ModuleName to FileSystem Location or Raise"""

    if (spec := importlib.util.find_spec(dot_path)) is None:
        raise ModuleNotFoundError(f"Missind Module: {dot_path=}")

    if spec.submodule_search_locations:
        return Path(next(iter(spec.submodule_search_locations))).resolve()

    if not spec.origin or spec.origin in {"built-in", "frozen"}:
        raise ValueError(f"Not found on Disk: {dot_path!r}!")

    return Path(spec.origin).resolve().parent


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
    """Walk upwards until next public Package"""  # AI: doc fine?

    parts: list[str] = module_name.split(".")

    while len(parts) > 1 and parts[-1].startswith("_"):
        parts.pop()

    return ".".join(parts)


@PathGuard.dir
def get_stub_dir(  # LATER: target:DotPathSpec?
    target: str | ModuleType | Path, subdir: str = "_stubs"
) -> Path:
    """Stable resolution of where stubs should live."""

    match target:
        case Path():
            base_dir: Path = target if target.is_dir() else target.parent
        case str():
            base_dir: Path = package_dir(target)
        case _:
            base_dir: Path = package_dir(module_name(target))

    return base_dir / subdir


def create_stub_files(
    obj: Any, *, prefix: str, package: str | None = None
) -> tuple[Path, Path]:
    """Generate target paths for internal stubs and package entrypoint stubs"""

    dot_path: str = package or public_package(module_name(obj))
    root: Path = package_dir(dot_path)
    project: Path = get_project_root()

    if not root.is_relative_to(project):
        raise ValueError(f"{root} is not inside project root {project}")

    # AI_QUESTION: what to ensure?
    # - what is the purpose in ensuring the file exists?
    # - isn't the file usually just overridden?
    # - for sure it must be writable, meaning parentdir, nothing to override
    # - unique increments will not help here, what about a backup strategy?

    stub_file = PathGuard.file(
        target=root / "_stubs" / f"_{prefix.lower()}.pyi",
        default_content=f"# Stub for {prefix}\n",
        raise_error=False,
    )
    # TASK: directly fill them in DTO, both in separate PathGuarded function
    # - check as well how and that to ensure the input is decisive enough

    init_stub = PathGuard.file(
        target=root / "__init__.pyi",
        default_content="# Package stubs\n",
        raise_error=False,
    )

    return stub_file, init_stub
