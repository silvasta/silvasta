"""
Define the Vertical Grid of the ColorPalette

-
"""

from enum import Enum, auto


class ColorPalette(Enum):
    """Define the Base Palette with 8 Colors"""

    CYAN = auto()
    GREEN = auto()
    RED = auto()
    YELLOW = auto()
    BLUE = auto()
    PURPLE = auto()
    BLACK = auto()
    WHITE = auto()

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> int:
        """Return the index of the ColorList"""
        return count

    def __call__(self) -> int:
        return self.value


x: int = ColorPalette.GREEN.value
y: int = ColorPalette.GREEN()

ROLES: list[str] = [
    "Title",
    "Success",
    "Warn",
    "Danger",
    "Path",
    "Special",
    "Break",
    "Info",
]

role: str = ROLES[ColorPalette.BLACK()]

blue: ColorPalette = ColorPalette.BLUE
path: str = ROLES[blue()]

SHORTCUTS: dict[str, ColorPalette] = {
    "c": ColorPalette.CYAN,
    "g": ColorPalette.GREEN,
    "r": ColorPalette.RED,
    "y": ColorPalette.YELLOW,
    "b": ColorPalette.BLUE,
    "p": ColorPalette.PURPLE,
    "s": ColorPalette.BLACK,
    "w": ColorPalette.WHITE,
}
