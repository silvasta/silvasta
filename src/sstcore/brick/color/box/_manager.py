"""
Create the internal turnstile that controls all colors

-
"""

from .._mappings import SHORTCUTS

__all__: list[str] = [
    "ColorHub",
]

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Self

from ....port.color import (
    Adapter,
    Color,
    ColorIdentifier,
    ColorManager,
    Painter,
    Palette,
)
from ._paint import PaintMill

StripLoader = Callable[
    [Adapter, Palette | str | None], Mapping[Color, Callable[[object], str]]
]


class ColorHub:
    """ColorManager impl: resolve + active strip + factory warm/clear."""

    def __init__(
        self,
        loader: StripLoader,
        *,
        factory: PaintMill | None = None,
        # factory: ColorFactory | None = None,
        active: Adapter = Adapter.CODE,
        palette: Palette | str | None = None,
    ) -> None:
        self._factory: PaintMill = factory or PaintMill()
        self._loader = loader
        self.active = active
        self._palette = palette
        self._theme_token = 0
        self._names: dict[str, Color] = {m.name.lower(): m for m in Color}
        self._aliases = {**SHORTCUTS}
        self._activate(active, palette)

    @classmethod
    def load(cls) -> Self:
        if cls._active is None:
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

    def resolve(self, target: ColorIdentifier) -> Color:
        if isinstance(target, Color):
            return target
        if isinstance(target, int):
            return Color(target)
        key = str(target).lower()
        if key in self._aliases:
            return self._aliases[key]
        try:
            return self._names[key]
        except KeyError as error:
            raise ValueError(f"unknown color: {target!r}") from error

    def painter(self, color: Color) -> Painter:
        # factory must already hold warm entries; get requires paint —
        # better: factory.get_cached or store strip and pass paint
        return self._factory_get(color)

    def _factory_get(self, color: Color) -> Painter:
        # Prefer factory API that can return warm cache without re-supplying paint:
        get_cached = getattr(self._factory, "cached", None)
        if get_cached is not None:
            return get_cached(self.active, color, self._theme_token)
        raise RuntimeError("factory missing cached() after warm()")

    def switch(self, adapter: Adapter) -> None:
        self._theme_token += 1  # optional: only bump on theme change
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
