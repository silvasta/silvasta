"""
Supply the Color and Tools with a nice public Interface

- ColorBox -> Colors (the protocol implementation)

"""

__all__: list[str] = [
    "Colors",
]


from ....port.calling import Stringable
from ....port.color import Color, ColorBox, ColorHub, ColorId, Painter
from ....port.link import portlink
from .._mappings import SHORTCUTS
from ._manager import ColorManager


@portlink(ColorBox)
class Colors:
    """Assembe and Orchestrate the Color Distribution"""

    def __init__(self, manager: ColorHub | None = None) -> None:
        self._hub: ColorHub = manager or ColorManager.boot()

    @property
    def hub(self) -> ColorHub:
        return self._hub

    def paint(self, color: ColorId) -> Painter:
        return self._hub.paint(Color.resolve(color))

    # NEXT: use brick.stack
    def __getattr__(self, name: str) -> Painter:
        if color := SHORTCUTS.get(name):
            return self.paint(color)

        if name in Color:
            return self.paint(name)

        raise AttributeError(f"{self} Missing Attribute: '{name}'!")

    def __call__(self, text: Stringable, color: ColorId) -> str:
        return self.paint(color)(text)
