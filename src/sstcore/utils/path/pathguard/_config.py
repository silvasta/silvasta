from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Self

type PathInput = Path | str | PathConfig


@dataclass(frozen=True, slots=True)
class PathConfig:
    """Encapsulates validation and normalization behaviors for a target path."""

    target: Path | str
    resolve: bool = False
    check_exists: bool = False
    must_exists: bool = False

    @classmethod
    def from_path_input(
        cls,
        path_input: PathInput | None = None,
        resolve: bool | None = None,
        check_exists: bool | None = None,
        must_exists: bool | None = None,
    ) -> Self:
        args: dict = {}

        if isinstance(path_input, PathConfig):
            args |= asdict(path_input)
        elif isinstance(path_input, (str, Path)):
            args["target"] = path_input
        elif path_input is None:
            args["target"] = Path.cwd()
        else:
            raise ValueError(f"Invalid {path_input=}")

        if resolve is not None:
            args["resolve"] = resolve
        if check_exists is not None:
            args["check_exists"] = check_exists
        if must_exists is not None:
            args["must_exists"] = must_exists

        return cls(**args)


class PathGuardState:
    """Internal thread-safe container for operational flags."""

    def __init__(self) -> None:
        self.debug: bool = True


_state = PathGuardState()
