"""
Unite all Path Tools under  PathGuard 

                               DependencyLevel.sstcore.util.path[0]
"""

__all__: list[str] = [
    "PathGuard",
]

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, overload

from ....error import PathGuardReason
from ....port.files import SyncMode
from .._pathcast import PathArg, PathSpec
from ._field import DirField, FileField, UniqueField

class PathGuard:
    Spec: type[PathSpec]
    SyncMode: type[SyncMode]
    Reason: type[PathGuardReason]

    @classmethod
    def toolkit(cls, sort: bool = True) -> list[str]: ...

    # -----------------------------------------------------------------------
    # Category 1: structural guards (hybrid call / decorator)
    # -----------------------------------------------------------------------

    @overload
    @staticmethod
    def dir(target: PathArg, /) -> Path: ...
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
        mode: str | SyncMode = SyncMode.INCREMENT,
        reset: bool = False,
    ) -> Path: ...
    @staticmethod
    def copy(
        source: PathArg,
        target: PathArg,
        mode: str | SyncMode = SyncMode.INCREMENT,
    ) -> Path: ...
    @staticmethod
    def hardlink(
        source: PathArg,
        target: PathArg,
        mode: str | SyncMode = SyncMode.INCREMENT,
    ) -> Path: ...
    @staticmethod
    def symlink(
        source: PathArg,
        target: PathArg,
        mode: str | SyncMode = SyncMode.INCREMENT,
    ) -> Path: ...
    @staticmethod  # CHECK:
    def backup(target: Path, /, suffix: str = ".bak") -> Path: ...

    # -----------------------------------------------------------------------
    # Category 3: relative helpers
    # -----------------------------------------------------------------------

    @overload
    @staticmethod
    def relative(
        target: PathArg,
        /,
        root: PathArg | None = None,
        strict: bool = True,
        *,
        existing: bool = False,
    ) -> Path: ...
    @overload
    @staticmethod
    def relative(
        target: Iterable[PathArg],
        /,
        root: PathArg | None = None,
        strict: bool = True,
        *,
        existing: bool = False,
    ) -> list[Path]: ...
    @overload
    @staticmethod
    def absolute(
        target: PathArg,
        /,
        root: PathArg | None = None,
        *,
        resolve: bool = True,
        must_exists: bool = False,
    ) -> Path: ...
    @overload
    @staticmethod
    def absolute(
        target: Iterable[PathArg],
        /,
        root: PathArg | None = None,
        *,
        resolve: bool = True,
        must_exists: bool = False,
        filter_exists: bool = False,
    ) -> list[Path]: ...
    @staticmethod
    def relative_duo(path1: PathArg, path2: PathArg) -> Path | None: ...
    @staticmethod
    def relative_string(source: PathArg, target: PathArg) -> str: ...
    @overload
    @staticmethod
    def split(
        target: PathArg,
        /,
        local_root: PathArg | None = None,
    ) -> tuple[Path, Path]: ...
    @overload
    @staticmethod
    def split(
        target: Iterable[PathArg],
        /,
        local_root: PathArg | None = None,
    ) -> list[tuple[Path, Path]]: ...
