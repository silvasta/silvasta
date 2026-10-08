"""
Construct Components, Bases and MetaMixins

- Prepare Views for (Static) Blueprints

"""

from typing import Any

__all__: list[str] = [
    "SstMeta",
    "SstMetaData",
]


from ....brick.color.box import Colors
from ....port.color import Color, ColorIdentifier
from ....port.link import portlink
from ....port.shape import Meta, MetaData

colors = Colors()  # LATER: resolve this somehows


@portlink(MetaData)
class SstMetaData:
    """Level 0 Mdto"""

    color: Color

    def __init__(self, color: ColorIdentifier = Color.AZURE):
        self.color: Color = Color.resolve(color)


@portlink(Meta)
class SstMeta(type):
    # CHECK: SstMeta.__init__? yes! and __call__, but later...
    """Level 0 Meta"""

    _data: SstMetaData

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: SstMetaData,
        # CHECK: destroy kwargs?
    ):
        cls = super().__new__(mcs, name, bases, namespace)
        cls._data = data
        return cls
