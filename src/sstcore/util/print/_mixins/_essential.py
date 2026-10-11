"""
Ensure pipeline arguments

- normalize: from Any type to stable string
- colorize: attach color and color combinations

Note:
  - still under construction
  - concept will change
"""

from sstcore.port.color import ColorBox, ColorId

__all__: list[str] = [
    "ColorBox",
    "NormalizeMixin",
]
from pathlib import Path
from typing import Any

from rich.console import ConsoleRenderable, RichCast

from ....brick.color import colorize
from ....brick.color.box import Colors
from ....port.calling import PydanticModel
from ....port.represent import Renderable


class NormalizeMixin:
    def normalize(self, target: Any) -> Renderable:  # NEXT: Renderable??
        """Normalize targets into renderable representations."""
        match target:  # TASK: find better check for this group
            case ConsoleRenderable() | RichCast() | str() | PydanticModel():
                return target
            case list() as items:
                return "\n".join(str(self.normalize(item)) for item in items)
            case Path() as path:
                return colorize.path(path)
            case _:
                return str(target)


class ColorMixin:
    colors: ColorBox

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors: ColorBox = Colors()

    @property
    def project_info(self) -> str:
        name: str = self.colors.azure(self.info.name)
        return f"{name} v{self.info.version}"

    # NEXT: ArgCast Color?
    def colorize(self, text: str, color: ColorId) -> str:
        return self.colors(text, color) if text else ""
