__all__: list[str] = [
    "PathSpec",
    "PathInput",
]

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

from ....exceptions import PathGuardError, PathGuardReason

type PathInput = str | Path | PathSpec


@dataclass(frozen=True, slots=True)
class PathSpec:
    """Normalize and Validate input for PathGuard execution"""

    target: Path

    resolve: bool = False
    # LATER: create entire grid of combined args?
    # - maybe with toggle, pick what to load and check before PathGuard
    must_exists: bool = False

    @classmethod
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
        if TYPE_CHECKING:
            # I really can't work with ty dimmed PathGuardError...
            target: Any = target

        kwargs: dict = {}

        if resolve is not None:
            kwargs["resolve"] = resolve
        if must_exists is not None:
            kwargs["must_exists"] = must_exists

        match target:
            case PathSpec():
                return cls(**{**asdict(target), **kwargs})
            case Path():
                return cls(target, **kwargs)
            case str():
                return cls(Path(target), **kwargs)
            case None:
                return cls(Path.cwd(), **kwargs)

        # TASK: __log__ DTO creation for direct attach in PathGuardError

        raise PathGuardError(
            reason=PathGuardReason.INPUT,
            target=target,
            prepared_kwargs=kwargs,
        )

    def validate(self) -> Path:
        """Ensure input Specification and provide Path"""

        path: Path = self.target

        if self.resolve:
            path: Path = path.resolve()

        if self.must_exists and not path.exists():
            raise PathGuardError(reason=PathGuardReason.MISSING, target=path)

        return path
