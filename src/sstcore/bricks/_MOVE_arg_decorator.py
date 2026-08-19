import functools
import inspect
from collections.abc import Callable
from typing import Any

from ..port.color import Color


def resolve_color(color_guess: Any, default: Color | None = None) -> Color:
    """Map [int|str|Color] to Color or default or Raise"""
    try:
        match color_guess:
            case Color():
                return color_guess

            case int() as index:
                return Color(index)

            case str() as name:
                return Color[name.upper()]

            case _:
                raise ValueError(f"Unrecognized type: {type(color_guess)}")

    except (ValueError, KeyError) as error:
        if default is not None:
            return default
        raise ValueError(f"Map Color failed: {color_guess=}") from error


def cast_color_args(func: Callable) -> Callable:
    """Normalize Color input based on type hints"""

    # TASK: Generlize!
    # - use Functor as Handler
    #   - include default
    #   - handle or execute error
    #   Idea1: (no inspect.*)
    #   - input: raw_value
    #   - output: result of resolve
    #   -> attach to bound_args
    #   Idea2: (with inspect)
    #   - input: param,bound_args,... or just send in all???
    #   - output: nothing if direct attach, or clean value
    # IDEA: make this a Functor Mixin!

    sig: inspect.Signature = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound_args: inspect.BoundArguments = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for name, param in sig.parameters.items():
            if param.annotation is Color:
                raw_value: Any = bound_args.arguments[name]
                try:
                    bound_args.arguments[name] = resolve_color(raw_value)
                except ValueError as error:
                    if param.default is not param.empty:
                        bound_args.arguments[name] = param.default
                    else:
                        raise ValueError(
                            f"Invalid input: {name!r} -> {raw_value!r}"
                        ) from error

        return func(*bound_args.args, **bound_args.kwargs)

    return wrapper


def _idea2_cast_color_args(func: Callable) -> Callable:
    sig = inspect.Signature.from_callable(func)
    color_params = {
        name
        for name, param in sig.parameters.items()
        if param.annotation is Color
    }

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for name in color_params:
            raw = bound.arguments[name]
            param = sig.parameters[name]
            default = (
                param.default if param.default is not param.empty else None
            )
            default_color = default if isinstance(default, Color) else None
            try:
                bound.arguments[name] = resolve_color(
                    raw, default=default_color
                )
            except ValueError as error:
                raise ValueError(
                    f"invalid color for {name!r}: {raw!r}"
                ) from error
        return func(*bound.args, **bound.kwargs)

    return wrapper
