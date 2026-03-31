from collections.abc import Callable
from pathlib import Path
from typing import ParamSpec, overload

P = ParamSpec("P")

class PathGuard:
    """Centralized path enforcement toolkit"""

    @staticmethod
    def _ensure_dir_logic(path: Path) -> Path: ...
    @overload
    @staticmethod
    def dir(target: Path) -> Path: ...
    @overload
    @staticmethod
    def dir(target: Callable[P, Path]) -> Callable[P, Path]: ...
    @staticmethod
    def dir(target: Callable[P, Path] | Path) -> Callable[P, Path] | Path: ...
    @staticmethod
    def _ensure_file_logic(
        path: Path,
        raise_error: bool = True,
        default_content: str | None = None,
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
        target: Path,
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> Path: ...
    @overload
    @staticmethod
    def file(target: Callable[P, Path]) -> Callable[P, Path]: ...
    @staticmethod
    def file(
        target: Callable[P, Path] | Path | None = None,
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> (
        Path
        | Callable[P, Path]
        | Callable[[Callable[P, Path]], Callable[P, Path]]
    ): ...
    @staticmethod
    def _get_unique_candidate(path: Path | str) -> Path: ...
    @overload
    @staticmethod
    def unique(target: Path) -> Path: ...
    @overload
    @staticmethod
    def unique(target: Callable[P, Path]) -> Callable[P, Path]: ...
    @staticmethod
    def unique(
        target: Callable[P, Path] | Path,
    ) -> Callable[P, Path] | Path: ...
    @staticmethod
    def find_sequence(base_target: Path) -> list[Path]: ...
    @staticmethod
    def prune(base_target: Path, remaining: int = 5) -> list[Path]: ...
    @staticmethod
    def rotate(
        source: Path | str, target: Path | str, reset: bool = False
    ) -> Path: ...
