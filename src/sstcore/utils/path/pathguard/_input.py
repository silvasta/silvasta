from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Self

type PathInput = Path | str | PathArg


@dataclass(frozen=True, slots=True)
# IDEA: PathTarget? yes but for func(target:PathTarget,source:PathTarget) ...?
class PathArg:  # NEXT: final name (and preferably checks below) error
    """
    Encapsulate Validation and Normalization behavior for Target

    Defines how the path should be interpreted and validated:
      - target: the path itself
      - resolve: whether to resolve symlinks and normalize
      - check_exists: whether existence is checked (but not required)
      - must_exists: whether the path *must* exist (strict mode)
    """

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

        if isinstance(path_input, PathArg):
            args |= asdict(path_input)
        elif isinstance(path_input, (str, Path)):
            args["target"] = path_input
        elif path_input is None:
            args["target"] = Path.cwd()
        else:  # LATER: custom error?
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
