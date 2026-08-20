"""
Prepare Cascade of Filters

- FilterData: Argument and Set Container and Modification without filtering
                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "FilterData",
]

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self

from ...port.filter import FilterSpec


@dataclass
class FilterData[SetType]:
    exclude: set[SetType] = field(default_factory=set)
    require_all: set[SetType] = field(default_factory=set)
    require_any: set[SetType] = field(default_factory=set)

    allow_hidden_files: bool = False
    return_opposite: bool = False

    @classmethod
    def from_args(cls, args: FilterSpec[SetType]) -> Self:
        return cls(
            exclude=set(args.exclude),
            require_all=set(args.require_all),
            require_any=set(args.require_any),
            allow_hidden_files=args.allow_hidden_files,
            return_opposite=args.return_opposite,
        )

    def merge(self, args: Self) -> Self:
        self.exclude.update(args.exclude)
        self.require_all.update(args.require_all)
        self.require_any.update(args.require_any)
        return self

    def subtract(self, args: Self) -> Self:
        self.exclude.difference_update(args.exclude)
        self.require_all.difference_update(args.require_all)
        self.require_any.difference_update(args.require_any)
        return self


if TYPE_CHECKING:
    _is_instance: FilterSpec = FilterData()
    _is_class: type[FilterSpec] = FilterData
