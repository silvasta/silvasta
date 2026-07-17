from dataclasses import dataclass, fields

from rich.theme import Theme

# NEXT: this as paint.py??

type ColorName = str

# TASK: as well stringly access to named colors
# required in PrintOption.grid ("blue" is still better than handover c.blue)
# - check render_table for desired usage


@dataclass(frozen=True)
class ThemeRole:
    """Binds a base theme color to its inverted counterpart."""

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

    # семантические роли
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
                # Export both formats for Rich markup support
                theme[field.name] = style.base
                theme[field.name.capitalize()] = style.inverted
            else:  # ensure string
                theme[field.name] = str(style)
        return theme

    def to_rich(self) -> Theme:
        """Dynamically export all colors and roles for rich.Theme"""
        return Theme(self.to_dict())


BASE_PALETTE = Palette()
