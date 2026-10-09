import functools
import inspect
from collections.abc import Callable
from typing import Annotated, Any, get_args, get_origin, get_type_hints

from ._port import Caster


def _get_caster(annotation: Any) -> Caster | None:
    """Extracts the first Caster from an Annotated type hint"""
    if get_origin(annotation) is Annotated:
        for meta in get_args(annotation)[1:]:
            if isinstance(meta, Caster) or callable(meta):
                return meta
    return None


def _get_plan(
    sig: inspect.Signature, hints: dict[str, Any]
) -> dict[str, Caster]:
    # MERGE: ArgCast.plan
    """Extracts the first Caster from an Annotated type hint"""

    plan: dict[str, Caster] = {}

    for name, param in sig.parameters.items():
        annotation = hints.get(name, param.annotation)
        if caster := _get_caster(annotation):
            plan[name] = caster
            continue  # AI: or break? why?

    return plan


def cast_args(func: Callable) -> Callable:
    # MERGE: ArgCast.__call__
    """Create optimized execution plan for runtime signature parsing"""

    sig: inspect.Signature = inspect.signature(func)
    hints: dict[str, Any] = get_type_hints(func, include_extras=True)
    plan: dict[str, Caster] = _get_plan(sig, hints)

    if not plan:
        # Zero overhead if no annotated casters are found
        return func

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound: inspect.BoundArguments = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        for name, caster in plan.items():
            raw_val = bound.arguments[name]
            param = sig.parameters[name]
            bound.arguments[name] = caster(raw_val, default=param.default)

        return func(*bound.args, **bound.kwargs)

    return wrapper
