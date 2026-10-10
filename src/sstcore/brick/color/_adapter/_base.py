"""
Create internal Color Schemes and Palettes

- Provide as well base functionalities for the adapter

"""

from src.sstcore.port.calling import Stringable

__all__: list[str] = [
    "ColorBlock",
    "PaletteDTO",
]

from dataclasses import dataclass
from typing import NamedTuple

from ....port.calling import Colorizing
from ....port.color import Color, ColorData, Coloring
from ....port.link import portlink


@portlink(ColorData)
@dataclass
class PaletteDTO:
    func: Coloring
    colors: ColorBlock

    def __post_init(self) -> None:
        print(f"loaded: {self=}")
        if len(self.colors) != len(Color):
            raise ValueError(f"Invalid colors... {self.colors=}, {Color=}")

    def bind(self, index: int, /) -> Colorizing:
        def colorizing(text: Stringable) -> str:
            return self.func(text, self.colors[index])

        return colorizing


# LATER: something like this
# class AdapterPalette(Palette):
#     def __init_subclass__(): ...


class ColorBlock(NamedTuple):
    """Define aligned Schema for Standard Colors"""

    green_: str
    teal__: str
    azure_: str
    blue__: str
    purple: str
    red___: str
    orange: str
    yellow: str
    white_: str
    slate_: str
    carbon: str
    black_: str

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(name.strip("_") for name in self._asdict().keys())

    @property
    def pairs(self) -> tuple[tuple[str, str], ...]:
        return tuple(
            (raw_key.strip("_"), value)
            for raw_key, value in self._asdict().items()
        )
