"""
Intercept Function Input and Apply Rules before Entry

- inspect typing.Annotated in signatures and extract rules
- unpack typing.TypedDict and apply rules to flattened params

What is the meaning of "cast" in this context?
- active process of enforcing rules to signatures
  (not equivalent to typing.cast but useful)

"""

__all__: list[str] = [
    "castarg",
    "ArgCast",
    "ArgCaster",
    "ArgCasting",
    "CastInput",
]

import functools
import inspect as _inspect
import typing as _t
from collections.abc import Callable
from inspect import BoundArguments, Signature
from typing import Any

from loguru import logger

from ...port._types import CallingTypes as _CT  # noqa: N814
from ...port._types import _ArgCasting as ArgCasting
from ...port.empty import VOID, MayBe
from ...port.link import portlink
from . import _cast


class ArgCast:
    """
    Cast Arguments in Function Signatures and Spec Mappings.

    Subclasses can register domain casters without instantiation:
        class PathCastPlugin(ArgCast, register={Path: PathCaster()}): ...
    """

    pass_defaults: bool = True
    _registry: _CT.CastRegistry = {}

    def __init__(self, *, pass_defaults: bool = True, **caster: ArgCasting):
        """Add predefined casters to use together with internal registry"""
        self.pass_defaults: bool = pass_defaults
        self.caster: _CT.CastPlan = caster

    def __contains__(self, target, /) -> bool:
        """Is the Target registered for Casting?"""
        return target in self._registry

    @classmethod
    def register(cls, key: Any, caster: ArgCasting, /) -> None:
        """Register single type caster directly"""
        if (old := cls._registry.get(key)) is not None:
            logger.debug(f"Replacing caster for {key!r}: {old!r} -> {caster!r}")
        cls._registry[key] = caster

    @classmethod
    def walk(cls, target: _CT.Castable, /) -> _CT.CastPlan:
        """Inspect Signature by walking all Params"""
        return _cast.build_plan(target, cls._registry)

    @classmethod
    def apply(cls, data: _CT.Data, target: _CT.Castable, /) -> _CT.Data:
        """Standalone helper: cast a kwargs dict against a Class/TypedDict/Func."""
        if plan := cls.walk(target):
            _cast.cast_mapping(plan, data)
        return data

    def __call__[**P, R](self, func: Callable[P, R]) -> Callable[P, R]:
        """Compile CastPlan once at Startup for continuous Execution"""

        if not (plan := self.walk(func) | self.caster):
            return func

        signature: Signature = _inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

            bound: BoundArguments = signature.bind(*args, **kwargs)

            if self.pass_defaults:
                bound.apply_defaults()

            _cast.param_spec(plan, bound)
            _cast.typed_dict(plan, bound)

            return func(*bound.args, **bound.kwargs)

        return wrapper


castarg = ArgCast()  # TARGET: Main Result


class CastInput[T](_t.TypedDict, total=False):
    """Base Input for TypedKwarg Pipeline"""

    default: MayBe[T]


@portlink(ArgCasting)
class ArgCaster[ArgSpace, Target]:
    """Orchestrate ArgCasting implementations"""

    input_types: _t.ClassVar[type | tuple[type, ...]] = object

    def __init__(self, default: MayBe[Target] = VOID, **kwargs):
        self.default: MayBe[Target] = default
        self.kwargs: dict[str, Any] = kwargs

    def cast(self, target: ArgSpace | Target | VOID, /) -> Target:
        """Subhook for Casting"""
        raise NotImplementedError(target)

    def aim(
        self, target: MayBe[ArgSpace], default: MayBe[Target] = VOID
    ) -> ArgSpace | Target | VOID:
        """Select target from Incoming Value, Signature- or Caster Default"""
        if target is VOID:
            return self.default if default is VOID else default
        if isinstance(target, self.input_types):
            return target
        return VOID

    def __call__(
        self,
        target: MayBe[ArgSpace] = VOID,
        /,
        *,
        default: MayBe[Target] = VOID,
    ) -> Target:
        """Aim for Target and execute Casting"""
        return self.cast(self.aim(target, default))
