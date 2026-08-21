"""
Define the Interface Colors and the Shape of the ColorBox

- Color:   All registered internal Colors       (c-axis of the grid)
- Adapter: All internal and external Adapters   (a-axis of the grid)
- Palette: 1-N Palettes all data of the Adapter (p-axis of the grid)

- ColorCoordinate: Navigate inside the 3d ColorGrid
- ColorIdentifier: Valid input types to get Color

-

- ColorManager: Connect Factory, Grid and Facade
- ColorBox: Provide Simple and Fast Color Supply

Ideas:
- ColorBus: global control of already distributed colors
"""

# TASK: fix last pieces, create the 3-axis And their spans:
# - Color-Adapter
# - Adapter-Schema
# - Schema-Color
# auto checks for standardized Palette by Color(Index) sizes,
# interface for Adapter including colors and tricks

__all__: list[str] = [
    "Color",
    "Adapter",
    "Palette",
    #
    "ColorData",
    "ColorFactory",
    "Painter",
    #
    "ColorIdentifier",
    "ColorCoordinate",
    "ColorRegistry",
    #
    "ColorManager",
    "ColorBox",
]


from enum import Enum, auto
from typing import NamedTuple, Protocol, Self, runtime_checkable

from .functional import Colorizing
from .view import Stringable


class GridIndex(Enum):  # WARN: fix index=0
    """Provide unique Base for Grid-Axes and Grid-Registries"""


type ColorIdentifier = int | str | Color


class Color(GridIndex):
    """Define the Base Palette with 12 indexed Colors"""

    WHITE = auto()
    BLACK = auto()
    BLUE = auto()
    GREEN = auto()
    YELLOW = auto()
    RED = auto()

    SLATE = auto()
    CARBON = auto()
    AZURE = auto()
    TEAL = auto()
    ORANGE = auto()
    PURPLE = auto()


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
    """Incoming Adapter Data ready to produce ColorPalette"""

    @property
    def func(self) -> Colorizing: ...
    @property
    def name(self) -> str: ...
    @property
    def colors(self) -> tuple[str, ...]: ...


class ColorPalette(ColorData, Protocol):
    painter: Painter

    @property
    def lookup(self) -> tuple[str, ...]: ...


class ColorFactory(Protocol):
    """Color Factory and Cache"""

    def provide(self, color: Color, palette: Palette) -> Painter: ...
    def setup(self, data: ColorData) -> ColorPalette:
        """Produce Numbered Palette of executable Colors out of Raw Data"""


@runtime_checkable
class Painter(Protocol):
    color: Color
    _paint: Colorizing
    """Lookup the current color code and paint"""

    def __call__(self, text: Stringable) -> str:
        """Apply the Colorizing function with lookup to ColorTable"""

    def __str__(self) -> str:
        """Return yourself"""


class ColorManager(Protocol):
    """Control the RuntimePalette and connect Grid, Factory and Box"""

    def painter(self, color: Color) -> Painter: ...
    def switch(self, adapter: Adapter) -> None: ...
    def set_palette(self, palette_id: Palette) -> None: ...
    def resolve(self, target: ColorIdentifier) -> Color: ...
    @classmethod
    def bootstrap(cls) -> Self: ...


class ColorCoordinate(NamedTuple):
    """Define a Point inside the ColorGrid"""

    c: Color
    a: Adapter
    p: Palette


class ColorRegistry(Protocol):  # TODO: Registry type
    """Define Schema with all Colors"""

    def __init__(self, c: Color, a: Adapter, p: Palette): ...


class ColorBox(Protocol):  # TASK: pyi with assigned color stacks
    """Global Orchestrator and Distributor of Colors"""

    def get(self, color: ColorIdentifier): ...

    def stack(self, *_args, **_kwargs):  # TODO:
        raise NotImplementedError

    def __getattr__(self) -> Painter:
        """Provide Colors on ColorIndex Name and Shortcut"""

    def __call__(self, text: Stringable, color: ColorIdentifier) -> str:
        # IDEA: return here painter!
        """Find Color by Identifier and return painted text"""

    def paint(self, color: ColorIdentifier) -> Painter | None:
        """Map ColorIndex to Painter of active Palette"""

    def index(self, target: str | Painter) -> Color | None:
        """Map Identifier or Painter to ColorIndex"""

    # REMOVE: when pyi fixed
    b: Painter
    g: Painter
    r: Painter
    y: Painter
    a: Painter
    t: Painter
    o: Painter
    p: Painter
    w: Painter
    s: Painter
    c: Painter
    d: Painter
    # REMOVE: when pyi fixed
    blue: Painter
    green: Painter
    red: Painter
    yellow: Painter
    azure: Painter
    teal: Painter
    orange: Painter
    purple: Painter
    white: Painter
    slate: Painter
    carbon: Painter
    black: Painter
    # REMOVE: when pyi fixed


class ColorBus(Protocol):
    """
    FUTURE IDEA: Keep control over any deployed color

    - With a simple implementation and local wiring
    - or as EventHandler of the global EventBus
    """
