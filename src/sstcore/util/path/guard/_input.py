"""
util.path.guard._input

-
"""

from dataclasses import asdict
from pathlib import Path
from typing import Annotated, Self, TypedDict, Unpack

from ....brick.call import ArgCast, ArgCaster, ArgCasting, CastInput
from ....error import PathGuardError, PathGuardReason
from ....port.empty import VOID, MayBe
from ....port.link import portlink
from ....port.structures import ArgSpec


class PathInput(TypedDict, total=False):
    resolve: bool
    must_exists: bool
    ensure_parent: bool


class PathCastInput(PathInput, CastInput[Path], total=False):
    """Extend Path with Default Casting Input"""


class PathSpec(ArgSpec[Path], frozen=True, slots=True):
    """Normalize and Validate input for PathGuard and Paths."""

    resolve: bool = False
    must_exists: bool = False
    ensure_parent: bool = False

    @classmethod
    def normalize(
        cls,
        target: MayBe[PathArg] = VOID,
        /,
        **kwargs: Unpack[PathInput],
    ) -> Self:
        if target is VOID:
            return cls(target=Path.cwd(), **kwargs)
        # if TYPE_CHECKING: # debug toggle
        #     target: Any = target
        match target:
            case PathSpec():
                return cls(**{**asdict(target), **kwargs})
            case Path():
                return cls(target=target, **kwargs)
            case str():
                return cls(target=Path(target), **kwargs)
        raise PathGuardError(PathGuardReason.INPUT, target, **kwargs)

    def validate(self) -> Path:
        path: Path = self.target
        if self.resolve:
            path = path.resolve()
        if self.must_exists and not path.exists():
            raise PathGuardError(reason=PathGuardReason.MISSING, target=path)
        if self.ensure_parent:
            path.parent.mkdir(parents=True, exist_ok=True)
        return path


type TargetPath = Annotated[Path, PathCaster()]
type SourcePath = Annotated[Path, PathCaster(must_exists=True)]
type ResolvedPath = Annotated[Path, PathCaster(resolve=True)]
type ResolvedSource = Annotated[
    Path, PathCaster(must_exists=True, resolve=True)
]
type ParentEnsuredPath = Annotated[Path, PathCaster(ensure_parent=True)]


PathArg = str | Path | PathSpec


@portlink(ArgCasting)
class PathCaster(ArgCaster[PathArg, Path]):
    input_types = (str, Path, PathSpec)

    def __init__(self, **kwargs: Unpack[PathCastInput]) -> None:
        super().__init__(**kwargs)

    def cast_target(self, target: MayBe[PathArg], /) -> Path:
        return PathSpec.ok(target, **self.kwargs)


ArgCast.register(Path, PathCaster())
ArgCast.register(PathArg, PathCaster())
