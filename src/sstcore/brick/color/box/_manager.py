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
from ._paint import ColorFactory


@portlink(ColorHub)
class ColorManager:
    """Manage the internal Turnstile that Controls the Colors"""

    def __init__(
        self, palette: Palette, factory: PaintMill | None = None
    ) -> None:
        self._factory: PaintMill = factory or ColorFactory()
        self._palette = palette

    @classmethod
    # AI: something like this, maybe the Meta Singleton Pattern
    def load(cls) -> Self:
        if cls._active is None:
            cls._active = cls.boot()
        return cls._active

    _active: Self | None = None

    @classmethod
    def boot(cls, *_args, **_kwargs) -> Self:
        raise NotImplementedError

    def paint(self, color: Color) -> Painter:
        return self._factory.paint(color, self._palette)

    def switch(self, palette: Palette):
        raise NotImplementedError(palette)
