"""
Define the Shape of the Arg Casting Pipeline

- Mount on functions and cast args

                                  DependencyLevel.sstcore.port[0.1]
"""

__all__: list[str] = [
    "ArgCasting",
    "CastInput",
    "CastPlan",
    "CastRegistry",
]

import typing as _t

from .empty import VOID, MayBe
from .structures import DataClassSpec, SpecMixin

type CastPlan = dict[str, ArgCasting]  # CHECK:
type CastRegistry = dict[_t.Any, ArgCasting]  # CHECK:

# AI_TASK: this collapsed quite heavily, ArgSpec could go back to port.structures._spec, what about the rest?
# - placing the ArgCasting and CastPlan/Registry in port.structures makes no sense...
# - the aliases could go to port._types, ArgCasting to brick.call?
# - the other approach is instead of resolving this filling it with more, what could be placed here?
# Discuss the options, consider port.structures as data structure module, where to place what?


class CastInput[T](_t.TypedDict, total=False):
    """Base Input for Typed Kwarg Pipeline"""

    default: MayBe[T]


class ArgSpec[T](SpecMixin, DataClassSpec, frozen=True):  # , slots=True):
    """Single-Target Validation with ArgCast"""

    target: T

    @classmethod
    def ok(cls, target: MayBe[_t.Any] = VOID, /, **kwargs) -> T:
        """Execute all Steps and provide confirmed Target"""
        return cls.normalize(target, **kwargs).validate()

    @classmethod
    def normalize(cls, target: MayBe[_t.Any] = VOID, /, **kwargs) -> _t.Self:
        """Create ArgSpec with confirmed Input"""
        raise NotImplementedError(target, kwargs)

    def validate(self) -> T:
        """Execute all Checks that the Target must fulfill"""
        return self.target


@_t.runtime_checkable
class ArgCasting[T = _t.Any](_t.Protocol):
    """Cast, Coerce, Resolve and/or Validate Function Input"""

    def __call__(self, target: _t.Any, /, *, default: MayBe[T] = VOID) -> T:
        """Validate Target in ArgCast-Pipeline"""
