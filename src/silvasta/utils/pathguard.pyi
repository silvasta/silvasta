from collections.abc import Callable
from pathlib import Path
from typing import Any, ParamSpec, overload

P = ParamSpec("P")

class PathGuard:
    """Centralized path enforcement toolkit"""

    @staticmethod
    def _ensure_input(
        path: Path | str,
        resolve: bool = False,
        check_exists: bool = False,
        must_exists: bool = False,
    ) -> Path: ...
    @staticmethod
    def _ensure_dir_logic(path: Path | str) -> Path: ...
    @overload
    @staticmethod
    def dir(target: Path | str) -> Path: ...
    @overload
    @staticmethod
    def dir(target: Callable[P, Path]) -> Callable[P, Path]: ...
    @staticmethod
    def dir(
        target: Callable[P, Path] | Path | str,
    ) -> Callable[P, Path] | Path: ...
    @staticmethod
    def _ensure_file_logic(
        path: Path | str,
        raise_error: bool,
        default_content: str | None,
    ) -> Path: ...
    @overload
    @staticmethod
    def file(
        target: None = None,
        *,
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> Callable[[Callable[P, Path]], Callable[P, Path]]: ...
    @overload
    @staticmethod
    def file(
        target: Path | str,
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> Path: ...
    @overload
    @staticmethod
    def file(target: Callable[P, Path]) -> Callable[P, Path]: ...
    @staticmethod
    def file(
        target: Callable[P, Path] | Path | str | None = None,
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> (
        Path
        | Callable[P, Path]
        | Callable[[Callable[P, Path]], Callable[P, Path]]
    ): ...
    @staticmethod
    def _get_unique_candidate(
        path: Path | str, ensure_parent: bool
    ) -> Path: ...
    @overload
    @staticmethod
    def unique(
        target: None = None,
        *,
        ensure_parent: bool = False,
    ) -> Callable[[Callable[P, Path]], Callable[P, Path]]: ...
    @overload
    @staticmethod
    def unique(target: Path | str, ensure_parent: bool = False) -> Path: ...
    @overload
    @staticmethod
    def unique(target: Callable[P, Path]) -> Callable[P, Path]: ...
    @staticmethod
    def unique(
        target: Callable[P, Path] | Path | str | None = None,
        ensure_parent: bool = False,
    ) -> (
        Path
        | Callable[P, Path]
        | Callable[[Callable[P, Path]], Callable[P, Path]]
    ): ...
    @staticmethod
    def find_sequence(base_target: Path | str) -> list[Path]: ...
    @staticmethod
    def prune(base_target: Path | str, remaining: int = 5) -> list[Path]: ...
    @staticmethod
    def rotate(
        source: Path | str, target: Path | str, reset: bool = False
    ) -> Path: ...
    @staticmethod
    def get_relative_or_name(
        target: Path | str,
        root: Path | str | None = None,
        check_exists: bool = False,
        must_exists: bool = False,
    ) -> str: ...
    @staticmethod
    def find_relative(
        target: Path | str,
        root: Path | str | None = None,
        check_exists: bool = False,
        must_exists: bool = False,
    ) -> Path | None: ...
    @staticmethod
    def compute_relative(
        target: Path | str,
        root: Path | str | None = None,
        check_exists: bool = False,
        must_exists: bool = False,
    ) -> Path: ...
    @staticmethod
    def relative_duo(
        path1: Path | str,
        path2: Path | str,
        check_exists: bool = False,
        must_exists: bool = False,
    ) -> Path | None: ...
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
