__all__: list[str] = [
    "PathGuard",
    "PathArg",
    "PathInput",
]
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import Any, overload

from ._input import PathArg, PathInput

class PathGuard:
    """Centralized path enforcement toolkit"""

    class SyncMode(StrEnum):
        INCREMENT = ...
        OVERRIDE = ...
        IGNORE = ...

        def check_conflict(self, target: Path) -> Path: ...

    PathArg = PathArg

    @staticmethod
    def debug(enable: bool) -> None: ...

    # --- Category 1: Structural Guards & Decorators ---
    @overload
    @staticmethod
    def dir(target: PathInput) -> Path: ...
    @overload
    @staticmethod
    def dir[**P](target: Callable[P, Path]) -> Callable[P, Path]: ...
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
    def file(
        target: PathInput,
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> Path: ...
    @overload
    @staticmethod
    def file[**P](target: Callable[P, Path]) -> Callable[P, Path]: ...
    @overload
    @staticmethod
    def unique[**P](
        target: None = None,
        *,
        ensure_parent: bool = False,
    ) -> Callable[[Callable[P, Path]], Callable[P, Path]]: ...
    @overload
    @staticmethod
    def unique(target: PathInput, ensure_parent: bool = False) -> Path: ...
    @overload
    @staticmethod
    def unique[**P](target: Callable[P, Path]) -> Callable[P, Path]: ...
    @staticmethod
    def find_sequence(base_target: PathInput) -> list[Path]: ...

    # --- Category 2: Maintenance & Destruction Ops ---
    @staticmethod
    def remove(target: PathInput) -> bool: ...
    @staticmethod
    def trash(target: PathInput) -> bool: ...
    @staticmethod
    def prune(
        base_target: PathInput, remaining: int = 5, trash: bool = False
    ) -> list[Path]: ...
    @staticmethod
    def rotate(
        source: PathInput,
        target: PathInput,
        sync_mode: str | SyncMode = "increment",
        reset: bool = False,
    ) -> Path: ...
    @staticmethod
    def copy(
        source: PathInput,
        target: PathInput,
        sync_mode: str | SyncMode = "increment",
    ) -> Path: ...
    @staticmethod
    def hardlink(
        source: PathInput,
        target: PathInput,
        sync_mode: str | SyncMode = "override",
    ) -> Path: ...
    @staticmethod
    def symlink(
        source: PathInput,
        target: PathInput,
        sync_mode: str | SyncMode = "increment",
    ) -> Path: ...

    # --- Category 3: Evaluators & Diagnostics ---
    @staticmethod
    def relative(
        target: PathInput,
        root: PathInput | None = None,
        strict: bool = True,
    ) -> Path: ...
    @staticmethod
    def relative_duo(
        path1: PathInput,
        path2: PathInput,
    ) -> Path | None: ...
    @staticmethod
    def relative_string(source: Path, target: Path) -> str: ...
    @overload
    @staticmethod
    def split_read_print_path(
        target: list[Path], local_root: Path | None = None
    ) -> list[tuple[Path, Path]]: ...
    @overload
    @staticmethod
    def split_read_print_path(
        target: Path, local_root: Path | None = None
    ) -> tuple[Path, Path]: ...
    @staticmethod
    def split_read_print_path(
        target: Any, local_root: Path | None = None
    ) -> list[tuple[Path, Path]] | tuple[Path, Path]: ...
