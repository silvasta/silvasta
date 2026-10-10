"""
Wire the ColorGrid with the Adapter, Factory, active Palette and Facade

- Collect and validate the values from the Adapter
- Order the Colors in the Factory including Cache
- Control the active Palette and apply changes (on request)
- Provide the ColorBox with the values for distribution

"""

__all__: list[str] = [
    "ColorManager",
]

from typing import Self

from ....port.color import Color, ColorHub, Painter, PaintMill, Palette
from ....port.link import portlink
from .._adapter._rich import RichPalette
from ._paint import ColorFactory


@portlink(ColorHub)
class ColorManager:
    """Manage the internal Turnstile that Controls the Colors"""

    def __init__(  # NOTE: factory ever needed to inject??
        self, palette: Palette, factory: PaintMill
    ) -> None:
        self._factory: PaintMill = factory or ColorFactory()
        self._palette: Palette = palette
        self._factory.setup(self._palette)

    @property
    def active(self) -> Palette:  # LATER: directly access self.palette
        return self._palette

    def paint(self, color: Color) -> Painter:
        return self._factory.paint(color, self._palette)

    def switch(self, palette: Palette):  # LATER: palette as Field?
        self._palette: Palette = palette
        self._factory.setup(palette)

    @classmethod
    def boot(cls, palette: Palette | None = None) -> Self:
        return cls(
            palette=palette or RichPalette(0),
            factory=ColorFactory(),
        )
