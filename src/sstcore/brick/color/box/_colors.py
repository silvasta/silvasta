"""
Supply the Color and Tools with a nice public Interface

- ColorBox -> Colors (the protocol implementation)

"""

__all__: list[str] = [
    "Colors",
]


from loguru import logger

from ....port.calling import Stringable
from ....port.color import Color, ColorBox, ColorHub, ColorId, Painter
from ....port.link import portlink
from .._mappings import SHORTCUTS
from ._manager import ColorManager


@portlink(ColorBox)
class Colors:
    """Assembe and Orchestrate the Color Distribution"""

    def __init__(self, *_args, **_kwargs) -> None:
        self._hub: ColorHub = ColorManager.boot()

    def __getattr__(self, name: str) -> Painter:
        if color := SHORTCUTS.get(name):
            return self.paint(color)

        if name in Color:
            return self.paint(name)

        raise AttributeError(f"{self} Missing Attribute: '{name}'!")

    def paint(self, color: ColorId) -> Painter:
        return self._hub.paint(Color.resolve(color))

    def __call__(self, text: Stringable, color: ColorId) -> str:
        return self.paint(color)(text)

    # NEXT: use brick.stack
    # def stack(self, *_args, **_kwargs) -> ColorStack:
    #     raise NotImplementedError

    @classmethod
    # REMOVE: colorbox is facade with many instances
    def set_active(cls, box: ColorBox) -> None:
        # MOVE: do this in the manager?
        # - spawn the facade everywhere without considering about others
        # - the manager handles and maybe the factory holds the active
        if cls._active is box:
            logger.info(f"Already set as global active Box: {box!r}")
        else:
            logger.info(f"New Box set as global active: {box!r}")
            cls._active = box
