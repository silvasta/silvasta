"""
collect

.
"""

from .config import LinkSpec
from .data import PortLinks, SidePolicy
from .define import Collecting
from .operator import ReflectorBase


class Reflect(ReflectorBase, id="reflector"):
    __call__: Collecting
    spec: LinkSpec  # IMPORTANT:
    nearest_target: type | None = None

    def __core__(self, port: type, plug: type, attr: str, /) -> PortLinks:  # ty:ignore
        data = PortLinks()
        self.walk_mro(data, attr, cls=plug, side=SidePolicy.PLUG, nearest=True)
        if self.nearest_target is None:
            self.emit(f"Missing ancestor {plug.__name__} for {attr=}")
            # IDEA: let it continure, and see what DocMerger prints
        self.walk_mro(data, attr, cls=port, side=SidePolicy.PORT)
        self.emit(f"Extracted __doc__: {len(data)}")
        return data

    def walk_mro(
        self,
        data: PortLinks,
        attr: str,
        *,
        cls: type,
        side: SidePolicy,
        nearest=False,
    ) -> None:
        for base in cls.__mro__:
            if self.spec.ignores(base):
                continue
            text: str = self.spawn.reflect().doc(base)
            if text and (attr, base) not in data:
                if nearest and side == SidePolicy.PLUG:
                    self.nearest_target: type = base
                    nearest = False
                data.fill(side.retrieve(text, attr, source=base))
