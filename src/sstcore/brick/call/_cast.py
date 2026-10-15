"""
Cast Function Input to Usable Input

- ArgCast: 1 member in the chain
- Todo: CastArg, collect multiple presets and apply ArgCast on __call__

"""

__all__: list[str] = [
    "ArgCaster",
    "ArgCast",
    "castarg",
]


import functools
import inspect as _i
from collections.abc import Callable
from typing import (
    Annotated,
    Any,
    Protocol,
    Unpack,
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


class ArgCast:
    """Execute Caster on Function Signature"""

    def __call__[**P, R](self, func: Callable[P, R]) -> Callable[P, R]:
        """Compile CastMap as plan for Casting"""

        if not (plan := self.plan(func)):
            return func

        sig: _i.Signature = _i.signature(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            bound: _i.BoundArguments = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            # 1. Cast regular positional/keyword parameters
            for name in plan.keys() & bound.arguments.keys():
                param_default = sig.parameters[name].default
                bound.arguments[name] = (
                    plan[name](bound.arguments[name])
                    if param_default is _i.Parameter.empty
                    else plan[name](
                        bound.arguments[name], default=param_default
                    )
                )

            # 2. Cast **kw: Unpack[TypedDict] arguments inside bound.kwargs
            if kw_dict := bound.kwargs:
                for key in plan.keys() & kw_dict.keys():
                    kw_dict[key] = plan[key](kw_dict[key])

            return func(*bound.args, **bound.kwargs)

        return wrapper

    @staticmethod
    def plan(target: Callable[..., Any] | type[Any]) -> dict[str, ArgCaster]:
        """Use reversed so the first Caster overwrites any subsequent ones"""
        return {
            name: meta
            for name, annotation in _iter_target_hints(target)
            if get_origin(annotation) is Annotated
            for meta in reversed(get_args(annotation)[1:])
            if isinstance(meta, ArgCaster) or callable(meta)
        }


castarg = ArgCast()  # TARGET: main object


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def extract_casters(
    target: Callable[..., Any] | type[Any],
) -> dict[str, ArgCaster]:
    """Extract {arg_name: caster} from any Function, Class, or TypedDict."""
    return {
        name: caster
        for name, hint in _iter_target_hints(target)
        if (caster := _first_caster(hint)) is not None
    }


def _first_caster(annotation: Any) -> ArgCaster | None:
    """Return the first callable/ArgCaster from Annotated[T, ...], or None."""
    if get_origin(annotation) is not Annotated:
        return None
    return next(
        (m for m in get_args(annotation)[1:] if callable(m)),
        None,
    )


def _iter_target_hints(target: Callable[..., Any] | type[Any]):
    """Yield (name, annotation) pairs, and unpack **kw: Unpack[TypedDict]"""
    for name, hint in get_type_hints(target, include_extras=True).items():
        if name == "return":
            continue
        if get_origin(hint) is Unpack:
            yield from get_type_hints(
                get_args(hint)[0], include_extras=True
            ).items()
        else:
            yield name, hint
