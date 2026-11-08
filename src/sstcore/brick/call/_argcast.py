"""
Intercept Function Input and Apply Rules before Entry

- inspect typing.Annotated in signatures and extract rules
- unpack typing.TypedDict and apply rules to flattened params

What is the meaning of "cast" in this context?
- active process of enforcing rules to signatures
  (not equivalent to typing.cast but useful)

"""

__all__: list[str] = [
    "ArgCast",
    "ArgCaster",
]

import functools
import inspect as _inspect
import typing as _t
from collections.abc import Callable, MutableMapping
from inspect import BoundArguments, Signature
from typing import Any

from loguru import logger

from ...port.casting import ArgCasting, CastPlan, CastRegistry
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
    _registry: CastRegistry = {}

    def __init__(self, *, pass_defaults: bool = True, **caster: ArgCasting):
        """Add predefined casters to use together with internal registry"""
        self.pass_defaults: bool = pass_defaults
        self.caster: CastPlan = caster

    def __contains__(self, target, /) -> bool:
        """Is the Target registered for Casting?"""
        return target in self._registry

    @classmethod
    def register(cls, key: Any, caster: ArgCasting, /) -> None:
        """Register single type caster directly"""
        if (old := cls._registry.get(key)) is not None:
            logger.debug(f"Replacing caster for {key!r}: {old!r} -> {caster!r}")
        cls._registry[key] = caster

    def _fallback(self, plan: CastPlan, name: str, annotation) -> None:
        # REMOVE: when walk resolved
        base = _t.get_args(annotation)[0]
        if caster := self._registry.get(base):
            plan[name] = caster

    @classmethod
    def walk(
        cls,
        target: Callable[..., Any] | type[Any],  # TODO: Alias?
        /,
    ) -> CastPlan:
        """Inspect Signature by walking all Params"""
        return _cast.build_plan(target, cls._registry)

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    @classmethod
    def mapping(
        cls,
        target: Callable[..., Any] | type[Any],  # TODO: Alias?
        data: MutableMapping[str, Any],
        /,
    ) -> MutableMapping[str, Any]:
        """Standalone helper: cast a kwargs dict against a Class/TypedDict/Func."""
        if plan := cls.walk(target):
            # AI_TASK: sync with execution in ArgCast.__call__
            # - idea is to have this exactly the same but with for separate execution
            _cast.cast_mapping(plan, data)
        return data

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __call__[**P, R](self, func: Callable[P, R]) -> Callable[P, R]:
        """Compile CastPlan once at Startup for continuous Execution"""

        plan: CastPlan = self.walk(func) | self.caster

        if not plan:
            return func

        signature: Signature = _inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

            bound: BoundArguments = signature.bind(*args, **kwargs)

            if self.pass_defaults:
                bound.apply_defaults()

            # AI: here 1-3 _cast.* desired (or in some collector function to share with ArgCast.mapping)
            _cast.param_spec(plan, bound, signature)
            _cast._typed_dict(plan, bound)  # FIX:

            return func(*bound.args, **bound.kwargs)

        return wrapper


castarg = ArgCast()  # TARGET: Main Result


@portlink(ArgCasting)
class ArgCaster[ArgSpace, Target]:
    """
    Reusable orchestration base for ArgCasting implementations.

    Handles `VOID` / `default` target resolution (`aim`) and delegates to `cast_target`.
    """

    input_types: _t.ClassVar[type | tuple[type, ...]] = object

    def __init__(self, default: MayBe[Target] = VOID, **kwargs):
        self.default: MayBe[Target] = default
        self.kwargs: dict[str, Any] = kwargs

    def __call__(
        self,
        target: MayBe[ArgSpace] = VOID,
        /,
        *,
        default: MayBe[Target] = VOID,
    ) -> Target:
        """Aim for Target and execute Casting"""
        selected: MayBe[ArgSpace | Target] = self.aim(target, default)
        return self.cast(selected)

    def aim(  # RENAME: ? annotate in Protocol?
        self, target: MayBe[ArgSpace], default: MayBe[Target] = VOID
    ) -> ArgSpace | Target | VOID:
        """Select target from Incoming Value, Signature- or Caster Default"""
        if target is VOID:
            return self.default if default is VOID else default
        if isinstance(target, self.input_types):
            return target
        return VOID

    def cast(self, target: ArgSpace | Target | VOID, /) -> Target:
        """Subhook for Casting"""
        raise NotImplementedError(target)
