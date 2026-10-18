"""
Create internal Color Schemes and Palettes

- Provide as well base functionalities for the adapter

"""

__all__: list[str] = [
    "ColorBlock",
    "PaletteDTO",
]

from dataclasses import dataclass
from typing import NamedTuple

from ....port.color import Color, ColorData, Coloring
from ....port.link import portlink


@portlink(ColorData)
@dataclass
class PaletteDTO:
    func: Coloring
    colors: ColorBlock

    def __post_init__(self) -> None:
        if len(self.colors) != len(Color):
            raise ValueError(f"Invalid colors... {self.colors=}, {Color=}")

        # TARGET:
        # print(f"{self}.[cyan]__post_init__()[/]{repr(self)}")
        # TARGET:

    def __str__(self):
        return f"{type(self).__name__}"

    def __repr__(self):
        _x = "-".join(f"{self.func(f'{c}', c)}" for c in self.colors)
        return f"[{_x}]"


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
