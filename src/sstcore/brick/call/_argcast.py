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
from collections.abc import Callable
from inspect import BoundArguments, Signature
from typing import Annotated, Any

from ...port.casting import ArgCasting, CastPlan, TypeRegistry
from . import _cast
from ._cast import iter_type_hints


class ArgCast:
    """Cast Arguments in Function Signature"""

    pass_defaults: bool = True  # CHECK: needed here?
    _registry: TypeRegistry = {}  # CHECK: on class or unit? most likely class
    # LATER: develop registry in forge.func with brick.vault.* + brick.call.*

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


castarg = ArgCast()  # TARGET: main result for export
