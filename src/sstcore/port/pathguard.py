from enum import StrEnum, auto
from pathlib import Path
from typing import Protocol, Self


class PathSpec(Protocol):
    """Normalize and validate input for PathGuard execution."""

    target: Path
    resolve: bool = False
    must_exists: bool = False

    @classmethod
    def ok(cls, *args, **kwargs) -> Path: ...
    @classmethod
    def normalized(cls, *args, **kwargs) -> Self: ...
    def validate(self) -> Path: ...


class SyncMode(StrEnum):
    """Govern the Conflict Resolution Strategy for File Transfers"""

    INCREMENT = auto()
    OVERRIDE = auto()
    IGNORE = auto()


class Transfering(Protocol):
    def __call__(self, source: Path, target: Path, mode: SyncMode) -> Path: ...


class PathGuard(Protocol):
    """
    Simple and Safe FileSystem Operations.

    - Check the PathGuard init and stub file for more information
    """

    Spec: type[PathSpec]
    SyncMode: type[SyncMode] = SyncMode
