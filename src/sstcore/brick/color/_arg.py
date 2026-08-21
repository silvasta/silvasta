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
