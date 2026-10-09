"""
Cast Function Input to Usable Input

- ArgCast: 1 member in the chain
- Todo: CastArg, collect multiple presets and apply ArgCast on __call__

"""

__all__: list[str] = [
    "ArgCast",
    "ArgCaster",
]


import functools
import inspect as _i
from collections.abc import Callable
from typing import (
    Annotated,
    Any,
    Protocol,
    get_args,
    get_origin,
    get_type_hints,
    runtime_checkable,
)


@runtime_checkable
class ArgCaster(Protocol):
    """Cast, Coerce, Resolve and or Validate the Function Input"""

    def __call__(
        self, value: Any, /, *, default: Any = _i.Parameter.empty
    ) -> Any: ...


class ArgCast[**P, R]:
    """Execute Caster on Function Signature"""

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        """Compile CastMap as plan for Casting"""

        if not (plan := self.plan(func)):
            return func

        sig: _i.Signature = _i.signature(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            bound: _i.BoundArguments = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for name, caster in plan.items():
                if name in bound.arguments:
                    bound.arguments[name] = caster(
                        bound.arguments[name],
                        default=sig.parameters[name].default,
                    )
            return func(*bound.args, **bound.kwargs)

        return wrapper

    @staticmethod
    def plan(func: Callable[..., Any]) -> dict[str, ArgCaster]:
        """Use reversed so the first Caster overwrites any subsequent ones"""
        sig: _i.Signature = _i.signature(func)
        hints: dict[str, Any] = get_type_hints(func, include_extras=True)
        return {
            name: meta
            for name, param in sig.parameters.items()
            if (annotation := hints.get(name, param.annotation))
            and get_origin(annotation) is Annotated
            for meta in reversed(get_args(annotation)[1:])
            if isinstance(meta, ArgCaster) or callable(meta)
        }
