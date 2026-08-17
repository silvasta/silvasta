"""
Assemble the Colors and Tools for public Representation

- ColorBox

"""

__all__: list[str] = [
    "Colors",
]
from typing import TYPE_CHECKING, Self

from loguru import logger

from ....helper import cls_name
from ....port.collections import Stringable
from ....port.color import (
    Color,
    ColorBox,
    ColorIdentifier,
    ColorManager,
    Painter,
)
from .._mappings import SHORTCUTS
from .._stack import ColorStack
from ._manager import ColorHub


class Colors:
    """Assembe and Orchestrate the Color Distribution"""

    # NEXT: init strategy

    def __init__(self, *_args, **_kwargs) -> None:
        self._hub: ColorManager = ColorHub.bootstrap()

    def __str__(self) -> str:
        return f"{cls_name(self)}[{self.active}]"

    def __getattr__(self, name) -> Painter | str:
        if color := SHORTCUTS.get(name):
            return self.color_to_paint(color)

        if name in Color:
            return self.color_to_paint(name)

        raise AttributeError(f"{self} Missing Attribute: '{name}'!")

    def color_to_paint(self, color: ColorIdentifier) -> Painter:
        # FIX:
        raise NotImplementedError(color)

    def resolve(self, target: ColorIdentifier) -> Color | None:
        # FIX:
        try:
            return self._hub.resolve(target)
        except ValueError:
            return None

    def __call__(self, text: Stringable, color: ColorIdentifier) -> str:
        """Paint text with identified Color"""
        # FIX:
        paint: Painter = self.get(color)
        return paint(text)

    def stack(self, *_args, **_kwargs) -> ColorStack:
        raise NotImplementedError

    @classmethod
    def load(cls) -> Self:
        if cls._active is None:
            cls._active = cls()
        return cls._active

    _active: ColorBox | None = None

    @classmethod
    def set_active(cls, box: ColorBox) -> None:
        if cls._active is box:
            logger.info(f"Already set as global active Box: {box!r}")
        else:
            logger.info(f"New Box set as global active: {box!r}")
            cls._active = box


if TYPE_CHECKING:
    _instance_check: Colors = ColorBox()
    _class_check: type[Colors] = ColorBox
