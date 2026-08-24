"""
Color Factory

- Paint: Attach Colors and Modifier on existing Functions
- PaintMill: Produce and Cache Colors for Painting

"""

__all__: list[str] = [
    "PaintMill",
    "Paint",
]

from collections.abc import Mapping
from typing import TYPE_CHECKING

from ....port.color import Adapter, Color, ColorFactory, Painter
from ....port.func import Colorizing, Stringable


class Paint(str):
    """Provide, be and apply the Color for one Value in the Palette"""

    __slots__ = ("color", "adapter", "_paint")

    def __new__(cls, color: Color, *_args, **_kwargs):
        return super().__new__(cls, color.name.lower())

    def __init__(self, color: Color, paint: Colorizing):
        self.color: Color = color
        self._paint: Colorizing = paint

        print(f"Created: {self} {self!r}")  # REMOVE:

    def __repr__(self) -> str:
        return f"{self}[{self.color!r}]"

    def __call__(self, text: Stringable) -> str:
        return self._paint(text)


if TYPE_CHECKING:
    _instance_check: Painter = Paint(Color.AZURE, lambda text: text)
    _class_check: type[Painter] = Paint


class PaintMill:
    """Produce Colors depending on Palette and Task"""

    def __init__(self) -> None:
        self._cache: dict[tuple[Adapter, Color, int], Paint] = {}

    def provide(
        self,
        color: Color,
        adapter: Adapter,
        paint: Colorizing,
        theme_token: int = 0,
    ) -> Painter:
        key = (adapter, color, theme_token)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        created = Paint(color, paint)
        self._cache[key] = created
        return created

    def warm(
        self,
        adapter: Adapter,
        paints: Mapping[Color, Colorizing],
        *,
        theme_token: int = 0,
    ) -> None:
        if len(paints) != len(Color):
            raise ValueError(
                f"expected {len(Color)} paints, got {len(paints)}"
            )
        for color, paint in paints.items():
            self.get(
                color, adapter=adapter, paint=paint, theme_token=theme_token
            )

    # TODO: NEEDED???
    def clear(self, adapter: Adapter | None = None) -> None:
        if adapter is None:
            self._cache.clear()
            return
        # WARN: this changes memory??!!??
        self._cache = {
            k: v for k, v in self._cache.items() if k[0] is not adapter
        }

    def __len__(self) -> int:
        return len(self._cache)


if TYPE_CHECKING:
    _instance_check: ColorFactory = PaintMill()
    _class_check: type[ColorFactory] = PaintMill
