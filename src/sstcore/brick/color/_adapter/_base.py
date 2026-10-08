"""
Create internal Color Schemes and Palettes

- Provide as well base functionalities for the adapter

"""

__all__: list[str] = [
    "ColorBlock",
    "PaletteDTO",
]

from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

from ....port.calling import Colorizing
from ....port.color import Color, ColorData


@dataclass
class PaletteDTO:
    func: Colorizing
    name: str
    colors: tuple[str, ...]

    def __post_init(self) -> None:
        if len(self.colors) != len(Color):
            raise ValueError(f"Invalid colors... {self.colors=}, {Color=}")


if TYPE_CHECKING:
    _test: type[ColorData] = PaletteDTO


class ColorBlock(NamedTuple):
    """Define numbered aligned Schema"""

    c0: str
    c1: str
    c2: str
    c3: str
    c4: str
    c5: str


def _format_named_blocks(*blocks: NamedTuple) -> tuple[tuple[str, str], ...]:
    return tuple(
        (raw_key.strip("_"), value)
        for block in blocks
        for raw_key, value in block._asdict().items()
    )


class ColorTuple(NamedTuple):
    def as_tuple_dict(self) -> tuple[tuple[str, str], ...]:
        return tuple(
            (raw_key.strip("_"), value)
            for raw_key, value in self._asdict().items()
        )


class _StandardBlock(ColorTuple):
    """Define aligned Schema for Standard Colors"""

    white_: str
    black_: str
    blue__: str
    green_: str
    yellow: str
    red___: str


x = _StandardBlock().as_tuple_dict()
y = x[1]


class StandardBlock(NamedTuple):
    """Define aligned Schema for Standard Colors"""

    white_: str
    black_: str
    blue__: str
    green_: str
    yellow: str
    red___: str


class CustomBlock(NamedTuple):
    """Define aligned Schema for Custom Colors"""

    slate_: str
    carbon: str
    azure_: str
    teal__: str
    orange: str
    purple: str


class _SemanticBlock(NamedTuple):
    alert__: Color
    danger_: Color
    error__: Color
    info___: Color
    special: Color
    success: Color
    title__: Color
