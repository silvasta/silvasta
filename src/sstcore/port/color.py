"""
Define the Interface Colors and the Shape of the ColorBox

- Color:   All registered internal Colors      (c-axis of the grid)
- Adapter: All internal and external Adapters  (a-axis of the grid)
- Palette: 1-N Palettes with all Adapter data  (p-axis of the grid)

- ColorCoordinate: Navigate inside the 3d ColorGrid
- ColorId: Valid input types to get Color

- ColorHub: Connect Factory, Grid and Facade
- ColorBox: Provide Simple and Fast Color Supply

Future Ideas:
- ColorBus: global control of already distributed colors


                                    DependencyLevel.sstcore.port[6]
"""

__all__: list[str] = [
    "Color",
    "Adapter",
    "Palette",
    #
    "ColorId",
    "ColorArg",
    "ColorCoordinate",  # CHECK: unused, needed? remove?
    #
    "Colorizing",
    "Coloring",
    #
    "ColorData",
    "ColorSchema",
    #
    "Painter",
    "ColorSchema",
    "PaintMill",
    #
    "ColorHub",
    "ColorBox",
]


from enum import auto
from typing import Annotated, NamedTuple, Protocol, Self

from .calling import Stringable  # 0
from .register import TupleRegister  # 5
from .solid import BaseEnum, EnumId  # 1


class GridIndex(BaseEnum, zero=True, walk=True):
    """
    Provide unique Base for Grid-Axes and Grid-Registries

    - zero=True -> auto starts numbering at 0 (=self.value)
    - walk=True -> meta walks mro to check for zero=True
    """


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


class Adapter(GridIndex):  # LATER: resolve with the palettes
    """Define the extension of Adapter Columns to the ColorGrid"""

    RICH = auto()
    ANSI = auto()
    HEX = auto()
    PLOT = auto()


class Palette(GridIndex):
    """Define one or multiple Palettes for the Adapter"""

    def data(self, *_args, **_kwargs) -> ColorData:
        """Provide the pre-processed data for the Factory"""
        # LATER: move this from all derivatives to some base:
        # return type(self)(0).data()
        raise NotImplementedError("Provide the related Color Data!")


type ColorId = EnumId[Color]
type ColorArg = Annotated[ColorId, Color.resolve]


class ColorCoordinate(NamedTuple):
    """Define a Point inside the ColorGrid"""

    c: Color
    a: Adapter
    p: Palette


class Coloring(Protocol):
    def __call__(self, text: Stringable, color: str, /) -> str:
        """Transform the Text into a Colored Renderable"""


class Colorizing(Protocol):
    def __call__(self, text: Stringable, /) -> str:
        """Apply Default or Bound Color to get Colored Renderable"""


class ColorData(Protocol):
    """Required Adapter Data Structure - ready to produce ColorSchema"""

    @property
    def func(self) -> Coloring: ...
    @property
    def colors(self) -> tuple[str, ...]: ...


class ColorSchema(Protocol):
    """Color Data Structure for Internal Cache"""

    def __init__(self, data: ColorData, /) -> None:
        """Process the DTO and setup the Schema"""

    @property
    def colors(self) -> TupleRegister[str]:
        """Interchangeable Lookup Table for Paints"""

    @property
    def paints(self) -> TupleRegister[Painter]:
        """Fixed Colorizer for Distribution"""

    def mount(self, index: int, /) -> Colorizing:
        """Bind Color and Coloring-Function to Colorizing Paints"""


class Painter(Protocol):
    color: Color
    _paint: Colorizing
    """Lookup the current color code and paint"""

    def __call__(self, text: Stringable) -> str:
        """Apply the Colorizing function with lookup to ColorTable"""

    def __str__(self) -> str:
        """Return yourself (...derive from str)"""


class PaintMill(Protocol):
    """Color Factory and Cache"""

    def setup(self, palette: Palette) -> ColorSchema:
        """Produce Numbered Palette of executable Colors out of Raw Data"""

    def paint(self, color: Color, palette: Palette) -> Painter:
        """Provide cached Colorizer for given (c,p)"""


class ColorHub(Protocol):
    """Control the RuntimePalette and connect Grid, Factory and Box"""

    def paint(self, color: Color) -> Painter:
        """Fetch cached Colorizer for given Color in active Palette"""

    def switch(self, palette: Palette) -> None:
        """Install given Palette by Setup or Fetch in Factory"""

    @classmethod
    def boot(cls) -> Self:
        """Start without any Configuration"""


class ColorBox(Protocol):  # TASK: pyi with assigned color stacks
    """Global Orchestrator and Distributor of Colors"""

    @property
    def hub(self) -> ColorHub:
        """Configuration access"""

    def paint(self, color: ColorId) -> Painter | None:
        """Map ColorIdentifier to Painter of active Palette"""

    def __getattr__(self, name: str) -> Painter:
        """Provide Colors on ColorIndex Name and Shortcut"""

    def __call__(self, text: Stringable, color: ColorId) -> str:
        """Find Color by Identifier and return painted text"""
