"""
Assemble the Colors and Tools for public Representation

- ColorBox

"""

__all__: list[str] = [
    "Colors",
]
from typing import TYPE_CHECKING

from loguru import logger

from ....port.color import (
    Color,
    ColorBox,
    ColorIdentifier,
    ColorManager,
    Painter,
)
from ....port.view import Stringable
from ...format import cls_name
from .._mappings import SHORTCUTS
from .._stack import ColorStack
from ._manager import ColorHub


class Colors:
    """Assembe and Orchestrate the Color Distribution"""

    # IMPORTANT: init strategy

    def __init__(self, *_args, **_kwargs) -> None:
        self._hub: ColorManager = ColorHub.bootstrap()

    def __str__(self) -> str:
        return f"{cls_name(self)}[{self.active}]"

    def __getattr__(self, name) -> Painter | str:
        if color := SHORTCUTS.get(name):
            return self.paint(color)

        if name in Color:
            return self.paint(name)

        raise AttributeError(f"{self} Missing Attribute: '{name}'!")

    def paint(self, color: ColorIdentifier) -> Painter:
        raise NotImplementedError(color)

    def index(self, target: ColorIdentifier | Painter) -> Color:
        raise NotImplementedError

    def __call__(self, text: Stringable, color: ColorIdentifier) -> str:
        raise NotImplementedError

    def stack(self, *_args, **_kwargs) -> ColorStack:
        raise NotImplementedError

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
