"""Define the Public Interface of PathGuard"""

__all__: list[str] = [
    "PathGuard",
    "PathSpec",
    "PathInput",
]

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import NoReturn, Self, overload

from ....error import PathGuardReason
from ....port.event.dto import LogDTO, PanelDTO

# ---------------------------------------------------------------------------
# Input layer (public)
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class PathSpec:
    """Normalize and validate input for PathGuard execution."""

    target: Path
    resolve: bool = False
    must_exists: bool = False

    @classmethod
    def ok(
        cls,
        target: PathInput | None = None,
        *,
        resolve: bool | None = None,
        must_exists: bool | None = None,
    ) -> Path:
        """Normalize + validate; return a concrete Path."""
        ...

    @classmethod
    def normalized(
        cls,
        target: PathInput | None = None,
        *,
        resolve: bool | None = None,
        must_exists: bool | None = None,
    ) -> Self:
        """Build a PathSpec from PathInput (with optional policy overrides)."""
        ...

    def validate(self) -> Path:
        """Apply resolve / must_exists policy; return Path."""
        ...

type PathInput = str | Path | PathSpec

# ---------------------------------------------------------------------------
# Nested enum (accessible as PathGuard.SyncMode; not a top-level export)
# ---------------------------------------------------------------------------

# AI: this is now as well in the sstcore.port.pathguard, expose here as well?
class SyncMode(StrEnum):
    """Conflict resolution strategy for transfer operations."""

    INCREMENT = "increment"
    OVERRIDE = "override"
    IGNORE = "ignore"

# ---------------------------------------------------------------------------
# Facade
# ---------------------------------------------------------------------------

class PathGuard:
    """
    Safety and comfort toolkit for path access and filesystem operations.

    Not instantiable — use class-level static API only.
    """

    Spec: type[PathSpec]
    SyncMode: type[SyncMode]
    Reason: type[PathGuardReason]

    def __init__(self) -> NoReturn:
        """PathGuard is not instantiable."""
        ...

    # --- metaclass view / introspection (PathGuardMeta) ---

    @classmethod
    def toolkit(cls, sort: bool = True) -> list[str]:
        """Names of all staticmethods on the toolkit."""
        ...

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

    # -----------------------------------------------------------------------
    # Category 1: structural guards (hybrid call / decorator)
    # -----------------------------------------------------------------------

    @overload
    @staticmethod
    def dir(target: PathInput) -> Path: ...
    @overload
    @staticmethod
    def dir[**P](target: Callable[P, Path]) -> Callable[P, Path]: ...
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
    def file[**P](
        target: None = None,
        *,
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> Callable[[Callable[P, Path]], Callable[P, Path]]: ...
    @overload
    @staticmethod
    def unique(target: PathInput, ensure_parent: bool = False) -> Path: ...
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
    def find_sequence(base_target: PathInput) -> list[Path]:
        """Sequence members for base path, newest mtime first."""
        ...

    # -----------------------------------------------------------------------
    # Category 2: transfer & delete
    # -----------------------------------------------------------------------

    @staticmethod
    def remove(target: PathInput) -> bool: ...
    @staticmethod
    def trash(target: PathInput) -> bool: ...
    @staticmethod
    def prune(
        base_target: PathInput,
        remaining: int = 5,
        *,
        use_trash: bool = False,
    ) -> list[Path]: ...
    @staticmethod
    def rotate(
        source: PathInput,
        target: PathInput,
        sync_mode: str | SyncMode = SyncMode.INCREMENT,
        reset: bool = False,
    ) -> Path: ...
    @staticmethod
    def copy(
        source: PathInput,
        target: PathInput,
        sync_mode: str | SyncMode = SyncMode.INCREMENT,
    ) -> Path: ...
    @staticmethod
    def hardlink(
        source: PathInput,
        target: PathInput,
        sync_mode: str | SyncMode = SyncMode.OVERRIDE,
    ) -> Path: ...
    @staticmethod
    def symlink(
        source: PathInput,
        target: PathInput,
        sync_mode: str | SyncMode = SyncMode.INCREMENT,
    ) -> Path: ...

    # -----------------------------------------------------------------------
    # Category 3: relative helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def relative(
        target: PathInput,
        root: PathInput | None = None,
        strict: bool = True,
    ) -> Path: ...
    @staticmethod
    def relative_duo(path1: PathInput, path2: PathInput) -> Path | None: ...
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
