"""
Color Factory

- Paint: Attach Colors and Modifier on existing Functions
- PaintMill: Produce and Cache Colors for Painting

"""

__all__: list[str] = [
    "PaintMill",
    "Paint",
]

from typing import ClassVar

from ....port.calling import Stringable
from ....port.color import (
    Color,
    ColorData,
    Coloring,
    Colorizing,
    ColorSchema,
    Painter,
    PaintMill,
    Palette,
)
from ....port.link import portlink
from ...vault import TupleVault


@portlink(Painter)
class Paint(str):
    """Provide, be and apply the Color for one Value in the Palette"""

    __slots__ = ("color", "adapter", "_paint")

    def __new__(cls, color: Color, /, *_args, **_kwargs):
        return super().__new__(cls, color.name.lower())

    def __init__(self, color: Color, paint: Colorizing):
        self.color: Color = color
        self._paint: Colorizing = paint

        print(f"Created: str({self}) repr({self!r})")  # REMOVE: after debug

    def __repr__(self) -> str:
        return f"{self}[{self.color!r}]"

    def __call__(self, text: Stringable, /) -> str:
        return self._paint(text)


@portlink(ColorSchema)
class ColorPalette:
    colors: TupleVault[str]
    paints: TupleVault[Painter]  # LATER: ReadOnlyField?

    def __init__(self, data: ColorData):
        """Prepare Painters with Lookups"""
        self.func: Coloring = data.func
        self.colors: TupleVault[str] = TupleVault(data.colors)
        self.paints: TupleVault[Painter] = TupleVault(
            Paint(color, paint=self.mount(color.value))  #
            for color in Color
        )

    def mount(self, index: int, /) -> Colorizing:

        def colorizing(text: Stringable) -> str:
            color: str = self.colors[index]
            return self.func(text, color)

        return colorizing


@portlink(PaintMill)
class ColorFactory:
    """Produce Colors depending on Palette and Task"""

    _cache: ClassVar[dict[Palette, ColorSchema]] = {}  # LATER: DictRegister

    def __init__(self, palette: Palette | None = None) -> None:
        if palette:
            self.setup(palette)

    def setup(self, palette: Palette) -> ColorSchema:
        # LATER: exchange theme if palette already in _cache
        if palette not in self._cache:
            self._cache[palette] = ColorPalette(palette.data())
        return self._cache[palette]

    def paint(self, color: Color, palette) -> Painter:
        if palette not in self._cache:
            self.setup(palette)
        return self._cache[palette].paints[color.value]

    def __len__(self) -> int:
        # LATER: more statistics function
        # - maybe __str__, __repr__ or some ColorFactory.show
        return len(self._cache)
