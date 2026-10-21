"""
Color Factory

- Paint: Attach Colors and Modifier on existing Functions
- PaintMill: Produce and Cache Colors for Painting

"""

from rich import print

__all__: list[str] = [
    "PaintMill",
    "Paint",
]

from typing import ClassVar

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
from ....port.represent import Stringable
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

        # TARGET:
        # print(f"[{self}]Created[/]::{self!r}")  # REMOVE: after debug
        # TARGET:

    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self}][{self._paint('painted')}]"

    def __call__(self, text: Stringable, /) -> str:
        return self._paint(text)


@portlink(ColorSchema)  # ty:ignore
class ColorPalette:
    colors: TupleVault[str]
    paints: TupleVault[Painter]  # LATER: ReadOnlyField?

    def __str__(self):
        return f"{type(self).__name__}"

    def __repr__(self):
        return f"{self}[({self.colors!r},{self.colors!r})]"

    def __init__(self, data: ColorData):
        """Prepare Painters with Lookups"""
        self.func: Coloring = data.func
        self.colors: TupleVault[str] = TupleVault(data.colors)

        # TARGET:
        # print("[bold red]Colors[/]")
        # for c in self.colors:
        #     print(f"[{c}]{self} loaded: {c}[/]")
        # TARGET:

        self.paints: TupleVault[Painter] = TupleVault(
            Paint(color, paint=self.mount(color.value))  #
            for color in Color
        )

        # TARGET:
        # print("[bold blue]Paints[/]")
        # for p in self.paints:
        #     print(p(f"paint ready: {p!r}"))
        # TARGET:

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

    def print(self):
        for k, v in self._cache.items():
            print(f"{k!r}: {v!r}")

    def setup(self, palette: Palette) -> ColorSchema:
        # LATER: exchange theme if palette already in _cache
        if palette not in self._cache:
            self._cache[palette] = ColorPalette(palette.data())  # ty:ignore
        return self._cache[palette]

    def paint(self, color: Color, palette) -> Painter:
        if palette not in self._cache:
            self.setup(palette)
        return self._cache[palette].paints[color.value]

    def __len__(self) -> int:
        # LATER: more statistics function
        # - maybe __str__, __repr__ or some ColorFactory.show
        return len(self._cache)
