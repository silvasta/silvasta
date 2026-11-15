"""
Define the Input Space including Widening, Normalization and Validation

-
"""

__all__: list[str] = [
    "PathSpec",
    "PathCaster",
    "PathArg",
    "PathInput",
    "PathCastInput",
    #
    "TargetPath",
    "SourcePath",
    "ResolvedPath",
    "ResolvedSource",
    "ParentEnsuredPath",
    "SinglePath",
    "MultiPath",
    "PathStrategy",
    # tests
    "is_singlepath",
    "is_singlepatharg",
    "is_multipath",
    "is_multipatharg",
]


from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import Annotated, Self, TypeIs
from typing import Unpack as _U  # noqa:N814

from typing_extensions import TypedDict

from ...brick.call import ArgCast, ArgCaster, ArgCasting, CastInput
from ...error import PathGuardError, PathGuardReason
from ...port.empty import VOID, MayBe
from ...port.link import portlink
from ...port.structures import ArgSpec


class PathInput(TypedDict, total=False):
    resolve: bool
    must_exists: bool
    ensure_parent: bool


class PathCastInput(PathInput, CastInput[Path], total=False, closed=True):
    """Extend Path with Default Casting Input"""


class PathSpec(ArgSpec[Path], frozen=True):
    """Normalize and Validate input for PathGuard and Paths."""

    resolve: bool = False
    must_exists: bool = False
    ensure_parent: bool = False

    @classmethod  # IMPORTANT:: use DataClassSpec.absorb??
    def normalize(
        cls, target: MayBe[PathArg] = VOID, /, **tkw: _U[PathInput]
    ) -> Self:
        if target is VOID:
            return cls(target=Path.cwd(), **tkw)
        match target:
            case cls():
                return target.evolve(**tkw)
            case Path():
                return cls(target=target, **tkw)
            case str():
                return cls(target=Path(target), **tkw)
        raise PathGuardError(PathGuardReason.INPUT, target, **tkw)

    def validate(self) -> Path:
        path: Path = self.target
        if self.resolve:  # NEXT: move somehow into normalize? diverges...
            path: Path = path.resolve()
        if self.must_exists and not path.exists():
            raise PathGuardError(reason=PathGuardReason.MISSING, target=path)
        if self.ensure_parent:
            path.parent.mkdir(parents=True, exist_ok=True)
        return path


PathArg = PathSpec | Path | str


def is_singlepath(target, /) -> TypeIs[Path]:
    return isinstance(target, (Path))


def is_singlepatharg(target, /) -> TypeIs[PathArg]:
    return isinstance(target, (PathArg))


def is_multipath(target, /) -> TypeIs[Iterator[Path]]:
    return all(isinstance(path, (Path)) for path in target)


def is_multipatharg(target, /) -> TypeIs[Iterator[PathArg]]:
    return all(isinstance(path, (PathArg)) for path in target)


@portlink(ArgCasting)
class PathCaster(ArgCaster[PathArg, Path]):
    _input_types = (PathSpec, Path, str)

    def __init__(self, **tkw: _U[PathCastInput]) -> None:
        super().__init__(**tkw)

    def cast(self, target: MayBe[PathArg], /) -> Path:
        return PathSpec.ok(target, **self.kwargs)


ArgCast.register(Path, PathCaster())
ArgCast.register(PathArg, PathCaster())


type TargetPath = Annotated[
    Path,
    PathCaster(),
]
type SourcePath = Annotated[
    Path,
    PathCaster(
        must_exists=True,
    ),
]
type ResolvedPath = Annotated[
    Path,
    PathCaster(
        resolve=True,
    ),
]
type ResolvedSource = Annotated[
    Path,
    PathCaster(
        must_exists=True,
        resolve=True,
    ),
]
type ParentEnsuredPath = Annotated[
    Path,
    PathCaster(
        ensure_parent=True,
    ),
]

# TODO: how to parametrize this ones times the ones above?
type SinglePath = PathArg
type MultiPath = Iterable[PathArg]
type PathStrategy = Callable[..., Path]
