# TODO: explain

# NEXT: this as paint.py??
from dataclasses import dataclass, fields

type ColorName = str

# NEXT: as well stringly access to named colors
# required in PrintOption.grid ("blue" is still better than handover c.blue)


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

    def to_rich_dict(self) -> dict[str, str]:
        """Dynamically export all colors and roles for rich.Theme"""
        rich_theme = {}
        for field in fields(self):
            val = getattr(self, field.name)
            if isinstance(val, ThemeRole):
                # Export both formats for Rich markup support
                rich_theme[field.name] = val.base
                rich_theme[field.name.capitalize()] = val.inverted
            else:
                rich_theme[field.name] = str(val)
        return rich_theme


BASE_PALETTE = Palette()
