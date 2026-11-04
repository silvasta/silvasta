__all__: list[str] = [
    "ArgCast",
    "castarg",
    "CastPlan",
]

import functools
import inspect as _inspect
from collections.abc import Callable, MutableMapping
from inspect import BoundArguments, Signature
from typing import Any, ClassVar

from ...port.casting import ArgCasting, CastPlan, TypeRegistry
from . import _caast


class ArgCast:
    """
    Cast Arguments in Function Signatures and Spec Mappings.

    Subclasses can register domain casters without instantiation:
        class PathCastPlugin(ArgCast, register={Path: PathCaster()}): ...
    """

    pass_defaults: bool = True
    _registry: ClassVar[TypeRegistry] = {}

    def __init_subclass__(
        cls,
        *,
        register: TypeRegistry | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        if register:
            cls._registry.update(register)

    def __init__(
        self, *, pass_defaults: bool | None = None, **overrides: ArgCasting
    ) -> None:
        if pass_defaults is not None:
            self.pass_defaults = pass_defaults
        self.overrides: CastPlan = overrides

    @classmethod
    def register(cls, target_type: Any, caster: ArgCasting, /) -> None:
        """Register a single type caster directly."""
        cls._registry[target_type] = caster

    @classmethod
    def casts(cls, target_type: Any, /) -> bool:
        """Check if type is registered for casting."""
        return target_type in cls._registry

    @classmethod
    def walk_plan(cls, target: Callable[..., Any] | type[Any], /) -> CastPlan:
        """Compile a CastPlan for a function, dataclass, or TypedDict."""
        return _caast.build_plan(target, cls._registry)

    @classmethod
    def cast_dict(
        cls,
        target: Callable[..., Any] | type[Any],
        data: MutableMapping[str, Any],
        /,
    ) -> MutableMapping[str, Any]:
        """Standalone helper: cast a kwargs dict against a Class/TypedDict/Func."""
        if plan := cls.walk_plan(target):
            _caast.cast_mapping(plan, data)
        return data

    def __call__[**P, R](self, func: Callable[P, R]) -> Callable[P, R]:
        """Compile CastPlan once at decoration time for continuous execution."""
        plan: CastPlan = self.walk_plan(func) | self.overrides

        if not plan:
            return func

        signature: Signature = _inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            bound: BoundArguments = signature.bind(*args, **kwargs)

            if self.pass_defaults:
                bound.apply_defaults()

            _caast.param_spec(plan, bound, signature)
            _caast.typed_dict(plan, bound, signature)

            return func(*bound.args, **bound.kwargs)

        return wrapper


castarg = ArgCast()
