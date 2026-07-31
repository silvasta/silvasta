"""
Apply Font Style

                                                       DependencyLevel[0]
"""

from dataclasses import dataclass, fields

from rich.theme import Theme

type ColorName = str

# AI_TASK: better access to all colors
# - there needs to be 1 controllable color source
# - around 10 colors and 6 named colors (e.g. the 6 below, title...)
# - A pallette must be like a replaceable part of the ColorBox
#   - switching themes or changing colors in the background,
#   while the effect in the front is only the changed color and not behaviour


@dataclass(frozen=True)
class ThemeRole:
    """Binds a base theme color to its inverted counterpart."""

    # AI: partially useful, this or something similar would be nice
    base: str
    inverted: str

    def __str__(self) -> str:
        return self.base


@dataclass(frozen=True)
class Palette:
    cyan: ColorName = "cyan"
    red: ColorName = "red"
    green: ColorName = "green"
    yellow: ColorName = "yellow"
    blue: ColorName = "blue"
    magenta: ColorName = "magenta"
    black: ColorName = "black"
    white: ColorName = "white"
    # orange, e.g.: dark_orange3
    # maybe gold3,steel_blue3

    title = ThemeRole(base="cyan", inverted="bold white on cyan")
    danger = ThemeRole(base="red", inverted="bold black on red")
    success = ThemeRole(base="green", inverted="bold white on green")
    warning = ThemeRole(base="yellow", inverted="bold black on yellow")
    special = ThemeRole(base="purple", inverted="bold white on purple")
    info = ThemeRole(base="white", inverted="black on white")

    def to_dict(self) -> dict[str, str]:
        """Dynamically export all colors and roles for rich.Theme"""
        theme: dict[str, str] = {}
        for field in fields(self):
            style: str | ThemeRole = getattr(self, field.name)
            if isinstance(style, ThemeRole):
                theme[field.name] = style.base
                theme[field.name.capitalize()] = style.inverted
            else:  # ensure string
                theme[field.name] = str(style)
        return theme

    def to_rich(self) -> Theme:
        """Dynamically export all colors and roles for rich.Theme"""
        return Theme(self.to_dict())


# AI: with that i display colors,
# - the ColorBox or Palette should not provide the prints,
# - but a list with formatted and colored strings
# def show_all_rich_colors():
#     logger.remove()
#     example: str = "This is how colored Text looks"
#     for color in rich_colors.keys():
#         target = f"{color} - {c(example, color)}"
#         printer.panel(target, frame=color)

BASE_PALETTE = Palette()
