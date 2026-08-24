"""
Pre-filter incoming args and provide clean input

- NOTE: placeholder until global location ready

"""

__all__: list[str] = [
    "resolve_color",
    "resolve_color_input",
]

from typing import Any

from ...port.color import Color


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


def resolve_color_input(default=Color.AZURE):
    # WARN: this is just a sketch, check ArgCast
    def arg_cast(color_guess: Any, *_, **__):
        return resolve_color(color_guess, default=default)

    return arg_cast
