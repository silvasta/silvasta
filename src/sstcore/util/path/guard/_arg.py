"""
Input Normalization

                         DependencyLevel.sstcore.util.path.guard[0]

"""

# NEXT: Decide which parts go to Base in brick.call._argcast or port.calling

__all__: list[str] = [
    "CastInput",
    "PathInput",
    "PathCastInput",
    "PathSpec",
    "PathArg",
    "PathCaster",
    "PathCast",
    "castpath",
    "MayBe",
    # annotated
    "TargetPath",
    "SourcePath",
    "ResolvedPath",
    "ResolvedSource",
    "ParentEnsuredPath",
]

import typing as _t
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import (
    Annotated,
    Any,
    Self,
    TypedDict,
    Unpack,
    reveal_type,
)

from ....brick.call import ArgCast, _cast
from ....error import PathGuardError, PathGuardReason
from ....port.casting import ArgCasting, CastInput, CastPlan, MayBe
from ....port.empty import VOID
from ....port.files import SyncMode
from ....port.link import portlink

type TargetPath = Annotated[Path, PathCaster()]
type SourcePath = Annotated[Path, PathCaster(must_exists=True)]
type ResolvedPath = Annotated[Path, PathCaster(resolve=True)]
type ResolvedSource = Annotated[
    Path, PathCaster(must_exists=True, resolve=True)
]
type ParentEnsuredPath = Annotated[Path, PathCaster(ensure_parent=True)]


class PathInput(TypedDict, total=False):
    """Configuration flags for PathSpec"""

    resolve: bool
    must_exists: bool
    ensure_parent: bool


class PathCastInput(PathInput, CastInput[Path], total=False):
    """Configuration flags for PathCaster"""


@dataclass(frozen=True, slots=True)
class PathSpec:
    """
    Normalize and Validate input for PathGuard and Paths

    - explicit value wrapper: PathSpec(path, resolve=True)
    - ArgCasting rule: Annotated[Path, PathSpec(must_exists=True)]

    """

    target: Path  # MOVE: to base

    resolve: bool = False
    must_exists: bool = False
    ensure_parent: bool = False

    def evolve(self, **kwargs) -> Self:  # MOVE: to base, if dataclass used
        return replace(self, **kwargs)

    @classmethod  # MOVE: to base
    def ok(
        cls,
        target: MayBe[PathArg] = VOID,
        /,
        **kwargs: Unpack[PathInput],
    ) -> Path:
        """Normalize and Validate Input to create PathSpec that is Okay"""

        return cls.normalize(target, **kwargs).validate()

    @classmethod
    def normalize(  # MOVE: maybe to base, provide subhooks
        cls,
        target: MayBe[PathArg] = VOID,
        /,
        **kwargs: Unpack[PathInput],
    ) -> Self:
        """
        Create PathSpec prepared with all arguments for Validation

        - target = None defaults to CWD
        - kwargs override incoming PathSpec

        """
        if target is VOID:
            # FIX: which?? return cls(target=Path.cwd(), **kwargs)
            raise PathGuardError(PathGuardReason.INPUT, target, **kwargs)

        match target:
            case PathSpec():
                return cls(**{**asdict(target), **kwargs})
            case Path():
                return cls(target, **kwargs)
            case str():
                return cls(target=Path(target), **kwargs)
            # case VOID:
            #     return cls(target=Path.cwd(), **kwargs)

        raise PathGuardError(PathGuardReason.INPUT, target, **kwargs)

    def validate(self) -> Path:  # MOVE: maybe to base, execute registry?
        """Ensure input Specification and provide resolved Path"""

        path: Path = self.target

        if self.resolve:
            path: Path = path.resolve()

        if self.must_exists and not path.exists():
            raise PathGuardError(reason=PathGuardReason.MISSING, target=path)

        if self.ensure_parent:
            path.parent.mkdir(parents=True, exist_ok=True)

        return path


PathArg = str | Path | PathSpec


@portlink(ArgCasting)
class PathCaster:
    def __init__(self, **kwargs: Unpack[PathCastInput]):
        """Prepare Input for Binding Args"""
        self.default: Any | VOID = kwargs.pop("default", VOID)
        self.kwargs: PathInput = kwargs

    def __call__(  # WARN: VOID/None for getting cwd or fail??
        self,
        target: MayBe[PathArg] = VOID,
        /,
        *,
        default: MayBe[Path] = VOID,
    ) -> Path:
        # MOVE: base for orchestration?
        """Prepare incoming Args and cast with PathSpec"""
        selected_target: MayBe[PathArg] = self.aim(target, default)
        return PathSpec.ok(selected_target, **self.kwargs)

    def aim(
        self, target: MayBe[PathArg], default: MayBe[Path] = VOID
    ) -> PathArg | VOID:
        # MOVE: base plus subhooks? or parameter on cls
        """Select Target from incoming target, default or saved default"""
        if target is VOID:
            if default is VOID:
                return self.default
            return default
        if isinstance(target, PathArg):
            return target
        return VOID


class PathCast(ArgCast):
    # NEXT: test the intersector
    """Specialized ArgCast with its own isolated path_registry and walk_plan."""

    def __init__(
        self, *, pass_defaults: bool | None = None, **overrides: PathCaster
    ):
        super().__init__(pass_defaults=pass_defaults, **overrides)
        self.path_registry: dict[Any, ArgCasting] = {
            Path: PathCaster(),
            PathArg: PathCaster(),
            SyncMode: _cast.sync_mode,
        }  # LATER: sync with ArgCast - global registry (plus local?)

    def casts(self, target_type, /) -> bool:  # MOVE: to base
        """Check if type is registered for casting"""
        return target_type in self.path_registry

    def _sync(self, plan: CastPlan, name: str, *, registry_lookup) -> None:
        # MOVE: to base, parametized
        """Update Plan with Caster of Registered Type"""
        plan[name] = self.path_registry[registry_lookup]

    def _fallback(self, plan: CastPlan, name: str, annotation):
        # MOVE: to base, parametized
        """Sync BaseType of Annotated[pos1] if Registered"""
        if self.casts(base_type := _t.get_args(annotation)[0]):
            self._sync(plan, name, registry_lookup=base_type)

    def walk_plan(self, target: Callable | type, /) -> CastPlan:
        # EXTRACT: template for ArgCast.walk
        """Match Annotations with Resolver or fallback to Registry"""

        plan: CastPlan = {}

        for name, annotation in _cast.iter_type_hints(target):
            if _t.get_origin(annotation) is Annotated:
                _cast.find_annotated_caster(plan, name, annotation)

                if name not in plan:
                    self._fallback(plan, name, annotation)

            elif self.casts(annotation):
                self._sync(plan, name, registry_lookup=annotation)

        return plan

    def intersect2(
        self,
        func: Callable[[Path], Path],
    ) -> Callable[[PathArg], Path]:
        # ) -> Callable[[Path], Path] & Callable[[PathArg], Path]:
        def wrapper(
            path: PathArg,
        ) -> Path:

            print("\nintersector::color:", end=" ")
            reveal_type(path)
            resolved: Path = PathSpec.ok(path)
            print("\nintersector::resolved:", end=" ")
            reveal_type(resolved)
            return func(resolved)

        reveal_type(wrapper)
        return wrapper

    # def intersect3[P = Path, Q = PathArg, R = Path](
    #     self,
    #     func: Callable[[P], R],
    # ) -> Callable[[P], R] & Callable[[Q], R]:
    #     # ) -> Callable[[Path], Path] & Callable[[PathArg], Path]:
    #     def wrapper(
    #         path: PathArg,
    #     ) -> Path:
    #
    #         print("\nintersector::color:", end=" ")
    #         reveal_type(path)
    #         resolved = PathSpec.ok(path)
    #         print("\nintersector::resolved:", end=" ")
    #         reveal_type(resolved)
    #         return func(resolved)
    #
    #     reveal_type(wrapper)
    #     return wrapper

    def intersect4(
        self, p1: Path, p2: Path
    ) -> Callable[[Callable[[Path], Path]], Callable[[PathArg], Path]]:
        # ) -> Callable[[Path], Path] & Callable[[PathArg], Path]:
        def deco(
            func: Callable[[Path], Path],
        ) -> Callable[
            [PathArg],
            Path,
        ]:
            def wrapper(
                path: PathArg,
            ) -> Path:
                resolved: Path = PathSpec.ok(path)

                print("\nintersector::color:", end=" ")
                reveal_type(path)
                print("\nintersector::resolved:", end=" ")
                reveal_type(resolved)
                return func(p1, p2)

            reveal_type(wrapper)
            return wrapper

        reveal_type(deco)
        return deco


castpath = PathCast()  # TARGET: usage inside Path.Guard
