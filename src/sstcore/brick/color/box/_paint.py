"""
Color Factory

- Paint: Attach Colors and Modifier on existing Functions
- PaintMill: Produce and Cache Colors for Painting

"""

from typing import ClassVar

__all__: list[str] = [
    "PaintMill",
    "Paint",
]


from ....port.calling import Colorizing, Stringable
from ....port.color import (
    Color,
    ColorData,
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

    def __call__(self, text: Stringable) -> str:
        return self._paint(text)


@portlink(ColorSchema)
class ColorPalette:
    colors: TupleVault[str]
    paints: TupleVault[Painter]

    def __init__(self, data: ColorData):
        """Prepare painters and loookups"""
        self.colors: TupleVault[str] = TupleVault(data.colors)
        self.paints: TupleVault[Painter] = TupleVault(
            Paint(color, paint=self.bind(color.value, data))  #
            for color in Color
        )

    def bind(self, index: int, data: ColorData, /) -> Colorizing:

        def colorizing(text: Stringable) -> str:
            color = self.colors[index]
            return data.func(text, color)

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
        return len(self._cache)
