"""
Unite all Path Tools under  PathGuard 

                               DependencyLevel.sstcore.util.path[0]
"""

__all__: list[str] = [
    "PathGuard",
    "StubFileGuard",
]

from collections.abc import Callable, Iterable
from pathlib import Path
from types import ModuleType
from typing import Any, NoReturn, overload

from ....error import PathGuardReason
from ....port.event.dto import LogDTO, PanelDTO
from ....port.files import SyncMode
from ._arg import PathArg, PathSpec
from ._field import DirField, FileField, UniqueField

# ---------------------------------------------------------------------------
# Input layer (public)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Mini
# ---------------------------------------------------------------------------

# NEXT: Move to own file??

class StubFileGuard:
    @staticmethod
    def module_name(obj: Any) -> str: ...
    @staticmethod
    def public_package(module_name: str) -> str: ...
    @staticmethod
    def package_dir(dot_path: str) -> Path: ...
    @staticmethod
    def stub_root(obj: Any, package: str | None = None) -> Path: ...
    @staticmethod
    def get_stub_dir(
        target: str | ModuleType | Path, subdir: str = "_stubs"
    ) -> Path: ...
    @staticmethod
    def stub_file_init(
        obj: Any, *, package: str | None = None, backup: bool = True
    ) -> Path: ...
    @staticmethod
    def single_stub_file(
        obj: Any,
        *,
        prefix: str,
        package: str | None = None,
        backup: bool = True,
    ) -> Path: ...

# ---------------------------------------------------------------------------
# Facade
# ---------------------------------------------------------------------------

class PathGuard:
    Spec: type[PathSpec]
    SyncMode: type[SyncMode]
    Reason: type[PathGuardReason]

    # EXTRACT: define at StaticMeta and mix it here?

    def __init__(self) -> NoReturn: ...
    @classmethod
    def __str__(cls) -> str: ...
    @classmethod
    def __repr__(cls) -> str: ...
    @classmethod
    def __rich__(cls) -> str: ...
    @classmethod
    def __cli__(cls) -> PanelDTO: ...
    @classmethod
    def __log__(cls) -> LogDTO: ...
    @classmethod
    def toolkit(cls, sort: bool = True) -> list[str]: ...

    # -----------------------------------------------------------------------
    # Category 1: structural guards (hybrid call / decorator)
    # -----------------------------------------------------------------------

    @overload
    @staticmethod
    def dir(target: PathArg) -> Path: ...
    @overload
    @staticmethod
    def dir[**P](target: Callable[P, Path]) -> Callable[P, Path]: ...
    @overload
    @staticmethod
    def file(
        target: PathArg,
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> Path: ...
    @overload
    @staticmethod
    def file[**P](target: Callable[P, Path]) -> Callable[P, Path]: ...
    @overload
    @staticmethod
    def file[**P](
        target: None = None,
        *,
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> Callable[[Callable[P, Path]], Callable[P, Path]]: ...
    @overload
    @staticmethod
    def unique(target: PathArg, ensure_parent: bool = False) -> Path: ...
    @overload
    @staticmethod
    def unique[**P](target: Callable[P, Path]) -> Callable[P, Path]: ...
    @overload
    @staticmethod
    def unique[**P](
        target: None = None,
        *,
        ensure_parent: bool = False,
    ) -> Callable[[Callable[P, Path]], Callable[P, Path]]: ...
    @staticmethod
    def find_sequence(base_target: PathArg) -> list[Path]:
        """Sequence members for base path, newest mtime first."""
        ...

    # -----------------------------------------------------------------------
    # Descriptors
    # -----------------------------------------------------------------------
    @overload
    @staticmethod
    def Dir(fget: Callable[[Any], Path]) -> DirField: ...
    @overload
    @staticmethod
    def Dir() -> Callable[[Callable[[Any], Path]], DirField]: ...
    @staticmethod
    def Dir(fget: Callable[[Any], Path] | None = None) -> Any: ...  # noqa: N802
    @overload
    @staticmethod
    def File(fget: Callable[[Any], Path]) -> FileField: ...
    @overload
    @staticmethod
    def File(
        *,
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> Callable[[Callable[[Any], Path]], FileField]: ...
    @staticmethod
    def File(  # noqa: N802
        fget: Callable[[Any], Path] | None = None, **policy: Any
    ) -> Any: ...
    @overload
    @staticmethod
    def Unique(fget: Callable[[Any], Path]) -> UniqueField: ...
    @overload
    @staticmethod
    def Unique(
        *,
        ensure_parent: bool = False,
    ) -> Callable[[Callable[[Any], Path]], UniqueField]: ...
    @staticmethod
    def Unique(  # noqa: N802
        fget: Callable[[Any], Path] | None = None, **policy: Any
    ) -> Any: ...
    # -----------------------------------------------------------------------
    # Category 2: transfer & delete
    # -----------------------------------------------------------------------
    @staticmethod
    def remove(target: PathArg) -> bool: ...
    @staticmethod
    def trash(target: PathArg) -> bool: ...
    @staticmethod
    def prune(
        base_target: PathArg,
        remaining: int = 5,
        *,
        use_trash: bool = False,
    ) -> list[Path]: ...
    @staticmethod
    def rotate(
        source: PathArg,
        target: PathArg,
        sync_mode: str | SyncMode = SyncMode.INCREMENT,
        reset: bool = False,
    ) -> Path: ...
    @staticmethod
    def copy(
        source: PathArg,
        target: PathArg,
        sync_mode: str | SyncMode = SyncMode.INCREMENT,
    ) -> Path: ...
    @staticmethod
    def hardlink(
        source: PathArg,
        target: PathArg,
        sync_mode: str | SyncMode = SyncMode.OVERRIDE,
    ) -> Path: ...
    @staticmethod
    def symlink(
        source: PathArg,
        target: PathArg,
        sync_mode: str | SyncMode = SyncMode.INCREMENT,
    ) -> Path: ...

    # -----------------------------------------------------------------------
    # Category 3: relative helpers
    # -----------------------------------------------------------------------

    @overload
    @staticmethod
    def relative(
        target: PathArg,
        root: PathArg | None = None,
        strict: bool = True,
    ) -> Path: ...
    @overload
    @staticmethod
    def relative(
        target: Iterable[PathArg],
        root: PathArg | None = None,
        strict: bool = True,
    ) -> list[Path]: ...
    @staticmethod
    def relative(
        target: PathArg | Iterable[PathArg],
        root: PathArg | None = None,
        strict: bool = True,
    ) -> Path | list[Path]: ...
    @overload
    @staticmethod
    def absolute(
        target: PathArg,
        root: PathArg | None = None,
        *,
        resolve: bool = True,
        must_exists: bool = False,
    ) -> Path: ...
    @overload
    @staticmethod
    def absolute(
        target: Iterable[PathArg],
        root: PathArg | None = None,
        *,
        resolve: bool = True,
        must_exists: bool = False,
        filter_exists: bool = False,
    ) -> list[Path]: ...
    @staticmethod
    def absolute(
        target: PathArg | Iterable[PathArg],
        root: PathArg | None = None,
        *,
        resolve: bool = True,
        must_exists: bool = False,
        filter_exists: bool = False,
    ) -> Path | list[Path]: ...
    @staticmethod
    def relative_duo(path1: PathArg, path2: PathArg) -> Path | None: ...
    @staticmethod
    def relative_string(source: Path, target: Path) -> str: ...
    @overload
    @staticmethod
    def split(
        target: Path,
        local_root: Path | None = None,
    ) -> tuple[Path, Path]: ...
    @overload
    @staticmethod
    def split(
        target: list[Path],
        local_root: Path | None = None,
    ) -> list[tuple[Path, Path]]: ...
