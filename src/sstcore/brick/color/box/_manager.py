"""
Wire the ColorGrid with the Adapter, Factory, active Palette and Facade

- Collect and validate the values from the Adapter
- Order the Colors in the Factory including Cache
- Control the active Palette and apply changes (on request)
- Provide the ColorBox with the values for distribution

"""

__all__: list[str] = [
    "ColorHub",
]

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Self, overload

from ....port.color import (
    Adapter,
    Color,
    ColorBox,
    ColorFactory,
    ColorIdentifier,
    ColorManager,
    Painter,
    Palette,
)
from .._arg import resolve_color_input
from ._paint import PaintMill

StripLoader = Callable[
    [Adapter, Palette | str | None], Mapping[Color, Callable[[object], str]]
]


class ColorHub:
    """Manage the internal Turnstile that Controls the Colors"""

    def __init__(
        self,
        # TASK: find proper adapter launch (maybe in facade)
        loader: StripLoader,
        *,
        factory: ColorFactory | None = None,
        active: Adapter = Adapter.ANSI,
        palette: Palette | str | None = None,
    ) -> None:
        self._factory: PaintMill = factory or PaintMill()
        self._loader = loader
        self.active = active
        self._palette = palette
        self._theme_token = 0
        self._activate(active, palette)

    @classmethod
    def load(cls) -> Self:
        if cls._active is None:
            # FIX:
            cls._active = cls()
        return cls._active

    _active: ColorBox | None = None

    @classmethod
    def boot(cls, *_args, **_kwargs) -> Self:
        raise NotImplementedError

    def _activate(
        self, adapter: Adapter, palette: Palette | str | None
    ) -> None:
        strip = self._loader(adapter, palette)
        self._factory.clear(adapter)
        self._factory.warm(adapter, strip, theme_token=self._theme_token)
        self.active = adapter
        self._palette = palette

    @overload
    def resolve(self, target: ColorIdentifier) -> Color: ...
    @overload
    def resolve(self, target: Color) -> Color: ...
    # MOVE: overload to .pyi such that it works well
    # (complains from type checker when final value != intersection of above)
    # - not here! but for distributed implementation at next change
    @resolve_color_input(default=Color.AZURE)
    def resolve(self, target: Color) -> Color:  # REMOVE:
        """No longer required on ColorManager, use ArgCast"""
        return target

    def painter(self, color: Color) -> Painter:
        return self._factory_get(color)

    def _factory_get(self, color: Color) -> Painter:
        get_cached = getattr(self._factory, "cached", None)
        if get_cached is not None:
            return get_cached(self.active, color, self._theme_token)
        raise RuntimeError("factory missing cached() after warm()")

    def switch(self, adapter: Adapter) -> None:
        self._theme_token += 1
        self._activate(adapter, self._palette)

    def set_palette(
        self, adapter: Adapter, palette_id: Palette | str | int
    ) -> None:
        self._theme_token += 1
        self._activate(
            adapter,
            palette_id if not isinstance(palette_id, int) else str(palette_id),
        )


if TYPE_CHECKING:
    _instance_check: ColorManager = ColorHub()
    _class_check: type[ColorManager] = ColorHub
