"""
Color Factory

- Paint: Attach Colors and Modifier on existing Functions
- PaintMill: Produce and Cache Colors for Painting

"""

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

    def __init__(self) -> None:  # LATER: DictRegister
        self._cache: dict[Palette, ColorSchema] = {}  # IDEA: classvar?

    def setup(self, palette: Palette) -> ColorSchema:
        # LATER: exchange theme, if palette in _cache...
        self._cache[palette] = (colors := ColorPalette(palette.data()))
        self._active = palette  # LATER: use this for self.paint?
        return colors

    def paint(self, color: Color, palette) -> Painter:
        return self._cache[palette].paints[color.value]

    def __len__(self) -> int:
        return len(self._cache)
