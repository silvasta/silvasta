"""
Apply Font Style

                                                       DependencyLevel[0]
"""

from dataclasses import dataclass, fields

from rich.theme import Theme


@dataclass(frozen=True)
class ThemeRole:
    """Binds a base theme color to its inverted counterpart."""

    # NEXT: this but 5 layer more, so far 8x2, target: 8x8
    # NEXT: this but 5 layer more
    # NEXT: this but 5 layer more

    base: str
    inverted: str

    def __str__(self) -> str:
        return self.base


@dataclass(frozen=True)
class Palette:
    cyan: str = "cyan"
    green: str = "green"
    red: str = "red"
    yellow: str = "yellow"

    magenta: str = "magenta"
    blue: str = "blue"

    black: str = "black"
    white: str = "white"
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


BASE_PALETTE = Palette()
