"""
Intercept Function Input and Apply Rules before Entry

- inspect typing.Annotated in signatures and extract rules
- unpack typing.TypedDict and apply rules to flattened params

What is the meaning of "cast" in this context?
- active process of enforcing rules to signatures
  (not equivalent to typing.cast but useful)

"""

from pathlib import Path

from loguru import logger

from src.sstcore.port.input import SpecBase
from src.sstcore.util.path.guard import PathArg

__all__: list[str] = [
    "ArgCast",
    "castarg",
    "CastPlan",
]


import functools
import inspect as _inspect
import typing as _t
from collections.abc import Callable
from inspect import BoundArguments, Parameter, Signature
from typing import Annotated, Any, ClassVar, Unpack

from ...port.casting import ArgCasting, CastPlan, TypeRegistry
from . import _cast
from ._cast import find_annotated_caster, iter_type_hints

# AI_TASK: this should end up as the executing base with all registered methods


class ArgCast:
    """Cast Arguments in Function Signature"""

    pass_defaults: bool = True
    _registry: TypeRegistry = {}  # NEXT: check HashedTuple

    def __init__(
        self, *, pass_defaults: bool | None = None, **overrides: ArgCasting
    ) -> None:
        if pass_defaults is not None:
            self.pass_defaults: bool = pass_defaults
        self.overrides: CastPlan = overrides

    def casts(self, target_type, /) -> bool:
        """Check if type is registered for casting"""
        return target_type in self._registry

    def __call__[**P, R](self, func: Callable[P, R]) -> Callable[P, R]:
        """Compile CastPlan once at Startup for continuous Execution"""

        plan: CastPlan = self.walk_plan(func) | self.overrides

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
            _cast.typed_dict(plan, bound)

            return func(*bound.args, **bound.kwargs)

        return wrapper

    @staticmethod
    def walk_plan(target: Callable[..., Any] | type[Any], /) -> CastPlan:
        """
        Map all Signatures to their Annotated resolver

        - reversed: first Caster overwrites any subsequent ones
        """
        return {  # LATER: decompose fragments and assemble, eg PathSpec
            name: caster
            for name, annotation in iter_type_hints(target)
            if _t.get_origin(annotation) is Annotated
            for caster in reversed(_t.get_args(annotation)[1:])
            if isinstance(caster, ArgCasting)
        }

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def _walk_plan(self, target, /) -> CastPlan:
        plan: CastPlan = {}
        for name, annotation in iter_type_hints(target):
            if _t.get_origin(annotation) is Annotated:
                find_annotated_caster(plan, name, annotation)
                if name not in plan:
                    self._fallback(plan, name, annotation)
            elif caster := self._registry.get(annotation):
                plan[name] = caster
        return plan

    @classmethod
    def register(cls, key: Any, caster: ArgCasting) -> None:
        if (old := cls._registry.get(key)) is not None:
            logger.debug(f"Replacing caster for {key!r}: {old!r} -> {caster!r}")
        cls._registry[key] = caster

    def _fallback(self, plan: CastPlan, name: str, annotation) -> None:
        base = _t.get_args(annotation)[0]
        if caster := self._registry.get(base):
            plan[name] = caster


castarg = ArgCast()  # TARGET: main result for export


# NEXT: useful?
class AutoCaster:
    """Кастер, который регистрирует свой экземпляр по умолчанию для объявленных типов."""

    casts_for: ClassVar[tuple[Any, ...]] = ()
    registry: ClassVar[TypeRegistry] = ArgCast._registry

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        if cls.casts_for:
            for key in cls.casts_for:
                cls.registry[key] = cls()


# util/path/guard/_input.py
class PathCaster(AutoCaster):
    casts_for = (Path, PathArg)


# NEXT:
def assert_sync(
    input_t: type[_t.TypedDict], spec_cls: type[SpecBase], /
) -> None:
    """Контракт времени разработки: поля TypedDict и Spec совпадают (запускать в тестах)."""
    input_keys = input_t.__required_keys__ | input_t.__optional_keys__
    if input_keys != spec_cls.field_names():
        raise TypeError(
            f"{input_t.__name__} <-> {spec_cls.__name__} drift: "
            f"{input_keys ^ spec_cls.field_names()}"
        )


# NEXT:
def mapping_plan(self, func) -> dict[str, ArgCasting]:
    """Кастеры уровня TypedDict для VAR_KEYWORD параметров."""
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
