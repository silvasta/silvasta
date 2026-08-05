from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, Self, overload


@dataclass
class FilterArgs[SetType]:
    exclude: set[SetType] = field(default_factory=set)
    require_all: set[SetType] = field(default_factory=set)
    require_any: set[SetType] = field(default_factory=set)

    allow_hidden_files: bool = False
    return_opposite: bool = False

    @classmethod
    def from_args(cls, args: FilterArgs) -> Self:
        return cls(
            exclude=set(args.exclude),
            require_all=set(args.require_all),
            require_any=set(args.require_any),
            allow_hidden_files=args.allow_hidden_files,
            return_opposite=args.return_opposite,
        )

    def merge(self, args: Self) -> Self:
        """Update internal sets with sets of incoming FilterArgs"""
        self.exclude.update(args.exclude)
        self.require_all.update(args.require_all)
        self.require_any.update(args.require_any)
        return self

    def subtract(self, args: Self) -> Self:
        """Update internal sets by removing incoming FilterArgs"""
        self.exclude.difference_update(args.exclude)
        self.require_all.difference_update(args.require_all)
        self.require_any.difference_update(args.require_any)
        return self


class Filter[SetType, TargetT](Protocol):
    """Define the shape of the FilterSet"""

    exclude: set[SetType]
    require_all: set[SetType]
    require_any: set[SetType]
    allow_hidden_files: bool
    return_opposite: bool

    @overload
    def __call__(self, target: SetType) -> bool: ...
    @overload
    def __call__(self, target: Iterable[TargetT]) -> list[TargetT]: ...
    def __call__(self, target: Any) -> bool | list[TargetT]:
        """Test a single item or filter a list"""

    def _create_target_set(self, target: Any) -> set[SetType]:
        """Turn an object into the set that will be matched against"""

    def _fulfills_conditions(
        self, target: Any, target_set: set[SetType]
    ) -> bool:
        """Override for custom validation logic."""

    def fulfills_exclude(self, target_set: set[SetType]) -> bool: ...
    def fulfills_require_all(self, target_set: set[SetType]) -> bool: ...
    def fulfills_require_any(self, target_set: set[SetType]) -> bool: ...
    def fulfills_condition_trio(self, target_set: set[SetType]) -> bool: ...


class Filterable[ItemT](Protocol):  # REMOVE: ??
    """Anything that can be asked: does this filter accept you?"""

    def __call__(self, filter: Filter[Any, ItemT]) -> bool: ...


class Filtering[ItemT](Protocol):
    """Mixin-style protocol for containers that can be filtered.

    Intended to be mixed into Registry implementations.
    """

    @property
    def filter(self) -> Filter[Any, ItemT] | None: ...

    def filtered(
        self, filter: Filter[Any, ItemT] | None = None
    ) -> list[ItemT]:
        """Return items that pass the given (or internal) filter"""


class PathFiltering(Filter[str, Path], Protocol):
    """Decomposes Path into parts/stem/suffix for filtering."""


class ProjectFiltering(PathFiltering, Protocol):
    """Project-specific defaults (exclude common dirs, require code files)."""
