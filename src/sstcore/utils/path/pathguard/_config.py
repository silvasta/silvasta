from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PathConfig:
    """Encapsulates validation and normalization behaviors for a target path."""

    target: Path | str
    resolve: bool = False
    check_exists: bool = False
    must_exists: bool = False


type PathInput = Path | str | PathConfig


class PathGuardState:
    """Internal thread-safe container for operational flags."""

    def __init__(self) -> None:
        self.debug: bool = True


_state = PathGuardState()
