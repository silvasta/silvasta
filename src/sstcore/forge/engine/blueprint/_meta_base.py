"""
Construct the MetaBase

-
"""

from typing import Any

__all__: list[str] = [
    "SstMeta",
    "SstMetaData",
]


from ....port.color import Color, ColorIdentifier
from ....port.link import portlink
from ....port.shape import Meta, MetaData


@portlink(MetaData)
class SstMetaData:
    """Level 0 Mdto"""

    color: Color

    def __init__(self, color: ColorIdentifier = Color.AZURE):
        self.color: Color = Color.resolve(color)


@portlink(Meta)
class SstMeta(type):
    """Level 0 Meta"""

    _data: SstMetaData

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: SstMetaData,
        # LATER: handle or destroy kwargs?
    ):
        cls = super().__new__(mcs, name, bases, namespace)
        cls._data = data
        return cls
