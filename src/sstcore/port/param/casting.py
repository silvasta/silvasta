"""
Define the Shape of the Arg Casting Pipeline

- Mount on functions and cast args

                              DependencyLevel.sstcore.port.empty[1]
"""

__all__: list[str] = [
    "ArgCasting",
    "CastInput",
    "CastPlan",
    "CastRegistry",
]

import typing as _t
from typing import Protocol as _Protocol

from ..empty import VOID, MayBe

type CastPlan = dict[str, ArgCasting]
type CastRegistry[T: _t.Any] = dict[T, ArgCasting]


class CastInput[Some](_t.TypedDict, total=False):
    """Configuration flags for ArgCasting"""

    default: Some | VOID


@_t.runtime_checkable
class ArgCasting[T = _t.Any](_Protocol):
    """Cast, Coerce, Resolve and/or Validate Function Input"""

    def __call__(self, target, /, *, default: MayBe[T] = VOID) -> T:
        """Cast, Coerce, Resolve and or Validate the Function Input"""
