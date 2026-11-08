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
    "castarg",
    "CastPlan",
]

import functools
import inspect as _inspect
import typing as _t
from collections.abc import Callable, MutableMapping
from inspect import BoundArguments, Parameter, Signature
from typing import Annotated, Any, Unpack

from loguru import logger

from . import cast as _cast
from .cast import find_annotated_caster
from .casting import ArgCasting, CastPlan, CastRegistry


class ArgCast:
    """
    Cast Arguments in Function Signatures and Spec Mappings.

    Subclasses can register domain casters without instantiation:
        class PathCastPlugin(ArgCast, register={Path: PathCaster()}): ...
    """

    pass_defaults: bool = True
    _registry: CastRegistry = {}  # NEXT: check HashedTuple like in CachedDataClassMeta._cache

    def __init_subclass__(  # REMOVE: ? maybe most simple with just the ArgCast.register?
        cls,
        *,
        register: CastRegistry | None = None,
        **kwargs: Any,
    ):
        """
        Subclasses can register domain casters without instantiation:

          - class PathCastPlugin(ArgCast, register={Path: PathCaster()}): ...
        """
        super().__init_subclass__(**kwargs)
        if register:
            cls._registry.update(register)

    def __init__(
        self, *, pass_defaults: bool | None = None, **overrides: ArgCasting
    ) -> None:
        if pass_defaults is not None:
            self.pass_defaults: bool = pass_defaults
        self.overrides: CastPlan = overrides

    def casts(self, target_type, /) -> bool:
        """Check if type is registered for casting"""
        return target_type in self._registry

    @classmethod
    def register(cls, key: Any, caster: ArgCasting, /) -> None:
        """Register a single type caster directly."""
        if (old := cls._registry.get(key)) is not None:
            logger.debug(f"Replacing caster for {key!r}: {old!r} -> {caster!r}")
        cls._registry[key] = caster

    def _fallback(self, plan: CastPlan, name: str, annotation) -> None:
        base = _t.get_args(annotation)[0]
        if caster := self._registry.get(base):
            plan[name] = caster

    @classmethod  # AI: can be as well regular method
    def walk(cls, *args, **kwargs) -> CastPlan:
        """Compile a CastPlan for a function, dataclass, or TypedDict or ..."""
        raise NotImplementedError(args, kwargs)

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    @classmethod
    def cast_dict(
        cls,
        target: Callable[..., Any] | type[Any],
        data: MutableMapping[  # AI: why MutableMapping? Move if not absolutely justified
            str, Any
        ],
        /,
    ) -> MutableMapping[str, Any]:
        """Standalone helper: cast a kwargs dict against a Class/TypedDict/Func."""
        if plan := cls.walk(target):
            _cast.cast_mapping(plan, data)
        return data

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __call__[**P, R](self, func: Callable[P, R]) -> Callable[P, R]:
        """Compile CastPlan once at Startup for continuous Execution"""

        plan: CastPlan = self.walk(func) | self.overrides

        if not plan:
            return func

        signature: Signature = _inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

            # IMPORTANT: expose logic for usage without decorator
            bound: BoundArguments = signature.bind(*args, **kwargs)

            if self.pass_defaults:
                bound.apply_defaults()

            _cast.param_spec(plan, bound, signature)
            _cast._typed_dict(plan, bound)

            return func(*bound.args, **bound.kwargs)

        return wrapper


castarg = ArgCast()  # TARGET: main result for export

# NEXT: decide or create catalog


def _walk(target: Callable[..., Any] | type[Any], /) -> CastPlan:
    """
    Map all Signatures to their Annotated resolver

    - reversed: first Caster overwrites any subsequent ones
    """
    return {  # LATER: decompose fragments and assemble, eg PathSpec
        name: caster
        for name, annotation in _cast._iter_type_hints(target)
        if _t.get_origin(annotation) is Annotated
        for caster in reversed(_t.get_args(annotation)[1:])
        if isinstance(caster, ArgCasting)
    }


def _walk(cls, target: Callable[..., Any] | type[Any], /) -> CastPlan:
    """Compile a CastPlan for a function, dataclass, or TypedDict."""
    return build_plan(target, cls._registry)


def build_plan(
    target: Callable[..., Any] | type[Any],
    registry: CastRegistry,
    /,
) -> CastPlan:
    """
    Match Annotations with explicit Annotated ArgCasting or fallback to Registry.

    Priority:
    1. First ArgCasting found in Annotated[T, ...] metadata
    2. Base type T of Annotated[T, ...] if T is in registry
    3. Direct annotation T if T is in registry
    """

    plan: CastPlan = {}

    for name, annotation in _cast._iter_type_hints(target):
        if _t.get_origin(annotation) is Annotated:
            _args = _t.get_args(annotation)
            # 1. Explicit caster in metadata
            for meta in _args[1:]:
                if isinstance(meta, ArgCasting):
                    plan[name] = meta
                    break
            else:
                # 2. Fallback to base type of Annotated[base_type, ...]
                if (base_type := _args[0]) in registry:
                    plan[name] = registry[base_type]

        # 3. Direct registered type (e.g., Path, PathArg, SyncMode, ColorArg)
        elif annotation in registry:
            plan[name] = registry[annotation]

    return plan


def _walk(self, func) -> dict[str, ArgCasting]:
    plan: dict[str, ArgCasting] = {}
    for name, param in _inspect.signature(func).parameters.items():
        if param.kind is not Parameter.VAR_KEYWORD:
            continue
        ann = param.annotation
        if _t.get_origin(ann) is Unpack and (
            c := self._registry.get(_t.get_args(ann)[0])
        ):
            plan[name] = c
    return plan


def _walk(self, target, /) -> CastPlan:
    plan: CastPlan = {}
    for name, annotation in _cast._iter_type_hints(target):
        if _t.get_origin(annotation) is Annotated:
            find_annotated_caster(plan, name, annotation)
            if name not in plan:
                self._fallback(plan, name, annotation)
        elif caster := self._registry.get(annotation):
            plan[name] = caster
    return plan
