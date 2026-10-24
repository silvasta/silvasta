"""
Construct the MetaBase

-
"""

from typing import Any

__all__: list[str] = [
    "SstMeta",
    "SstMetaData",
]


from ...port.color import Color, ColorId
from ...port.link import portlink
from ...port.shape import Meta, MetaData


@portlink(MetaData)
class SstMetaData:
    """Level 0 Mdto"""

    color: Color

    def __init__(self, color: ColorId = Color.AZURE):
        self.color: Color = Color.resolve(color)


@portlink(Meta)
class SstMeta(type):
    """Level 0 Meta"""

    _data: SstMetaData
    data_type: type[SstMetaData] = SstMetaData

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: SstMetaData,  # AI: only 1 way to insert param allowed, by the DTO
    ):
        cls = super().__new__(mcls, name, bases, namespace)
        cls._data = data
        return cls
