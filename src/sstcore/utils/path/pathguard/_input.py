__all__: list[str] = [
    "PathSpec",
    "PathInput",
]

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Self

from ....exceptions import PathGuardError, PathGuardReason

type PathInput = str | Path | PathSpec


@dataclass(frozen=True, slots=True)
class PathSpec:
    """Normalize and Validate input for PathGuard execution"""

    path: Path

    resolve: bool = False
    must_exists: bool = False
    # LATER: create entire grid? maybe with toggle, what to load/check before PathGuard
    # - parent_exists -> only create directory tree up to 1 level higher

    @classmethod
    # AI_QUESTION: this as something like callback on PathGuard functions for directly parsing input args?
    def ok(
        cls,
        target: PathInput | None = None,
        *,
        resolve: bool | None = None,
        must_exists: bool | None = None,
    ) -> Path:
        """Confirm that input is valid. (stack both main functions)"""
        path_spec: Self = cls.normalized(
            target,
            resolve=resolve,
            must_exists=must_exists,
        )
        return path_spec.validate()

    @classmethod
    def normalized(
        cls,
        target: PathInput | None = None,
        *,
        resolve: bool | None = None,
        must_exists: bool | None = None,
    ) -> Self:
        """
        Create PathSpec() with prepared arguments for validation

        - Filter toggled input settings and create Kwargs
        - Normalize to Path and create PathSpec with Kwargs
        - Override attributes of incoming PathSpec with Kwargs

        """
        kwargs: dict = {}

        if resolve is not None:
            kwargs["resolve"] = resolve
        if must_exists is not None:
            kwargs["must_exists"] = must_exists

        match target:
            case PathSpec():
                path: Path = target.path  # NOTE: ensure with this
                kwargs: dict = {**asdict(target), **kwargs}
                kwargs.pop("target")
                # return cls(**{**asdict(target), **kwargs}) # option
            case Path():
                path = target
            case str():
                path = Path(target)
            case None:  # AI: valid?
                path: Path = Path.cwd()  # NEXT: needed?
            case _:
                # FIX: ty(v0.0.63) shadows everything grey here
                # - exception badly visible...
                # ├╴  Code is unreachable
                # │    This may depend on your current environment and settings ty  [55, 17]
                raise PathGuardError(
                    reason=PathGuardReason.BAD_INPUT,
                    target=target,
                    prepared_kwargs=kwargs,
                )

        return cls(path, **kwargs)

    def validate(self) -> Path:
        """Ensure input Specification and provide Path"""

        path: Path = self.path

        if self.resolve:
            path: Path = path.resolve()

        if self.must_exists and not self.path.exists():
            raise PathGuardError(reason=PathGuardReason.MISSING, target=path)

        return path

    # LATER:
    # TASK: __log__ DTO creation for direct attach in PathGuardError
