"""
Define the Shape of the Arg Casting Pipeline

- Mount on functions and cast args

                              DependencyLevel.sstcore.port.empty[1]
"""

__all__: list[str] = [
    "ArgCasting",
    "CastInput",
    # types
    "CastPlan",
    "TypeRegistry",
]

import dataclasses as _dc
import typing as _t
from typing import Protocol as _Protocol

from .empty import VOID, MayBe

type CastPlan = dict[str, ArgCasting]
type TypeRegistry[T: type] = dict[T, ArgCasting]


class CastInput[Some](_t.TypedDict, total=False):
    """Configuration flags for ArgCasting"""

    default: Some | VOID


@_t.runtime_checkable
class ArgCasting[Some = _t.Any](_Protocol):
    """Cast, Coerce, Resolve and/or Validate Function Input"""

    def __call__(self, target, /, *, default: MayBe[Some] = VOID) -> Some:
        """Cast, Coerce, Resolve and or Validate the Function Input"""


@_t.dataclass_transform(kw_only_default=True)
class ArgSpecBase:
    # LATER: compare with EventDTO::ParamSpec, Functor::BaseParamSpecfind,
    """Setup Base for Input sanitizing DataClasses"""

    def __init_subclass__(cls, kw_only: bool = True, **kwargs):
        super().__init_subclass__(**kwargs)
        _dc.dataclass(kw_only=kw_only, **kwargs)(cls)


class ArgSpec[T](ArgSpecBase):
    # AI: so far unsure how useful this base is...

    target: T

    def evolve(self, **kwargs) -> _t.Self:
        return _dc.replace(self, **kwargs)

    @classmethod
    def ok(cls, target: MayBe[T] = VOID, /, **kwargs) -> T:
        # FAIL: how to assing TypedDict to kwargs in derived class?
        # (without writing everything again...)
        """Normalize and Validate Input to create PathSpec that is Okay"""
        return cls.normalize(target, **kwargs).validate()

    @classmethod
    def normalize(cls, target: MayBe[T] = VOID, /, **kwargs) -> _t.Self:
        # TODO: some subhooks?
        return cls(target=target, **kwargs)

    def validate(self) -> T:
        """Ensure input Specification and provide resolved Path"""
        return self.target
