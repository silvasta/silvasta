"""
Define the Interface Colors and the Shape of the ColorBox

- Color:   All registered internal Colors       (c-axis of the grid)
- Adapter: All internal and external Adapters   (a-axis of the grid)
- Palette: 1-N Palettes all data of the Adapter (p-axis of the grid)

- ColorCoordinate: Navigate inside the 3d ColorGrid
- ColorId: Valid input types to get Color

- ColorHub: Connect Factory, Grid and Facade
- ColorBox: Provide Simple and Fast Color Supply

Future Ideas:
- ColorBus: global control of already distributed colors


                                    DependencyLevel.sstcore.port[6]
"""

from src.sstcore.port.register import TupleRegister

__all__: list[str] = [
    "Color",
    "Adapter",
    "Palette",
    "ColorData",
    #
    "Painter",
    "ColorSchema",
    "PaintMill",
    #
    "ColorId",
    "ColorCoordinate",
    #
    "ColorHub",
    "ColorBox",
]


from enum import auto
from typing import NamedTuple, Protocol, Self

from ._enum import EnumId  # 0
from .calling import Colorizing, Stringable  # 0
from .solid import BaseEnum  # 1


class GridIndex(BaseEnum, zero=True, walk=True):
    """Provide unique Base for Grid-Axes and Grid-Registries"""


class Color(GridIndex):
    """Define the Base Palette with 12 Colors"""

    GREEN = auto()
    TEAL = auto()
    AZURE = auto()
    BLUE = auto()
    PURPLE = auto()
    RED = auto()
    ORANGE = auto()
    YELLOW = auto()
    WHITE = auto()
    SLATE = auto()
    CARBON = auto()
    BLACK = auto()


type ColorId = EnumId[Color]


class Adapter(GridIndex):
    """Define the extension of Adapter Columns to the ColorGrid"""

    RICH = auto()
    ANSI = auto()
    HEX = auto()
    PLOT = auto()


class Palette(GridIndex):
    """Define one or multiple Palettes for the Adapter"""

    def data(self, *_args, **_kwargs) -> ColorData:
        """Provide the pre-processed data for the Factory"""
        raise NotImplementedError("Provide the related Color Data!")


class ColorData(Protocol):
    """Incoming Adapter Data ready to produce ColorSchema"""

    @property
    def func(self) -> Coloring: ...
    @property
    def colors(self) -> tuple[str, ...]: ...


class Coloring(Protocol):
    def __call__(self, text: Stringable, color: str, /) -> str:
        """Apply handed in Color to Text"""


class ColorSchema(Protocol):
    """Transform the Adapter Data to internal Structure"""

    @property
    def colors(self) -> TupleRegister[str]:
        """The lookup table for the painters"""

    @property
    def paints(self) -> TupleRegister[Painter]:
        """The prepared colorizing functions with lookup"""

    def bind(self, index: int, data: ColorData, /) -> Colorizing:
        """Bind Color to internal Coloring"""


class Painter(Protocol):
    color: Color
    _paint: Colorizing
    """Lookup the current color code and paint"""

    def __call__(self, text: Stringable) -> str:
        """Apply the Colorizing function with lookup to ColorTable"""

    def __str__(self) -> str:
        """Return yourself"""


class PaintMill(Protocol):
    """Color Factory and Cache"""

    def setup(self, palette: Palette) -> ColorSchema:
        """Produce Numbered Palette of executable Colors out of Raw Data"""

    def paint(self, color: Color, palette: Palette) -> Painter: ...


class ColorHub(Protocol):
    """Control the RuntimePalette and connect Grid, Factory and Box"""

    def paint(self, color: Color) -> Painter: ...
    def switch(self, palette: Palette) -> None: ...
    @classmethod
    def boot(cls) -> Self:
        """Start without any Configuration if needed"""


class ColorCoordinate(NamedTuple):
    """Define a Point inside the ColorGrid"""

    c: Color
    a: Adapter
    p: Palette


class ColorBox(Protocol):  # TASK: pyi with assigned color stacks
    """Global Orchestrator and Distributor of Colors"""

    def __getattr__(self, name: str) -> Painter:
        """Provide Colors on ColorIndex Name and Shortcut"""

    def __call__(self, text: Stringable, color: ColorId) -> str:
        """Find Color by Identifier and return painted text"""

    def paint(self, color: ColorId) -> Painter | None:
        """Map ColorIndex to Painter of active Palette"""
