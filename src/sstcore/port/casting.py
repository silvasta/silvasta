"""
Define the Shape of the Arg Casting Pipeline

- Mount on functions and cast args

                             DependencyLevel.sstcore.port.empty[10] 🙂
"""

__all__: list[str] = [
    "ArgCasting",
    "SpargCasting",
    "CastInput",
    # types
    "CastPlan",
    "TypeRegistry",
]

import typing as _t
from typing import Any
from typing import Protocol as _Protocol

from .empty import VOID, MayBe

type CastPlan = dict[str, ArgCasting]
type TypeRegistry[T: type] = dict[T, ArgCasting]


class CastInput[Some](_t.TypedDict, total=False):
    """Configuration flags for ArgCasting"""

    default: Some | VOID


@_t.runtime_checkable
class ArgCasting[Some = Any](_Protocol):
    """Check if target can be used for ArgCast pipeline"""

    def __call__(self, target, /, *, default: MayBe[Some] = VOID) -> Some:
        """Cast, Coerce, Resolve and or Validate the Function Input"""


@_t.runtime_checkable
class SpargCasting[Result = Any, Raw = Any](_Protocol):
    """Cast, Coerce, Resolve and/or Validate Function Input."""

    def __call__(
        self, target: Result | Raw, /, *, default: MayBe[Result] = VOID
    ) -> Result: ...
