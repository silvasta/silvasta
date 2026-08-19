from typing import TYPE_CHECKING, Self

from ....port.color import Color, Painter
from .._adapter import PaletteDTO

# TASK: fix this for combinatorial grids!


class PaintPalette(PaletteDTO):
    painter: Painter
    lookup: tuple[str, ...]

    @classmethod
    def from_data(
        cls,
        data: PaletteDTO,
        painter: Painter,
        lookup: tuple[str, ...],
    ) -> Self:
        return cls(
            func=data.func,
            name=data.name,
            colors=data.colors,
            painter=painter,
            lookup=lookup,
        )


from enum import StrEnum, auto


class TextStyle(StrEnum):
    # TODO: here or in adapter? per adapter??!!
    NORMAL = auto()
    BOLD = auto()
    DIM = auto()
    REVERSE = auto()  # renders not nicely...

    # LATER: check:
    # "frame": "frame",
    # "encircle": "encircle",
    # "overline": "overline",

    def to_rich(self) -> str:
        return {
            self.NORMAL: "",
            self.BOLD: "bold",
            self.DIM: "dim",
            self.REVERSE: "reverse",
        }[self]


class ColorPalette:
    """Fixed-length schematic palette for one adapter."""

    __slots__ = ("adapter", "_cells", "_settings")

    def __init__(
        self,
        adapter: ColorAdapter,
        cells: Sequence[Cell],  # len == 12
        settings: AdapterSettings | None = None,
    ) -> None:
        if len(cells) != len(ColorIndex):
            raise ValueError(
                f"Expected {len(ColorIndex)} cells, got {len(cells)}"
            )
        self.adapter = adapter
        self._cells: tuple[Cell, ...] = tuple(cells)
        self._settings = settings or AdapterSettings()

    def get(self, color: ColorIndex) -> Any:
        cell = self._cells[color.value]
        return cell() if callable(cell) else cell

    def paint_for(self, color: ColorIndex) -> Formatting:
        raw = self.get(color)
        return _default_paint(raw)  # adapter subclasses override

    def with_settings(self, settings: AdapterSettings) -> ColorPalette:
        """Theme switch without rebuilding cell identities."""
        return ColorPalette(self.adapter, self._cells, settings)


class ColorPalette:
    """Provide the schematic Color implementation for one Adapter"""

    values: tuple[str | Callable | Color | Any, ...]  # TODO:
    adapter: ColorAdapter

    def get(self, color: ColorIndex) -> Any:
        """Simply return the prepared VALUES inside the tuple"""
        return self.values[color.value]


if TYPE_CHECKING:
    _instance_check: ColorSchema = ColorPalette()
    _class_check: type[ColorSchema] = ColorPalette

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
