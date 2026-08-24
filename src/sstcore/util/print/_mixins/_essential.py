"""
Ensure pipeline arguments

- normalize: from Any type to stable string
- colorize: attach color and color combinations

Note:
  - still under construction
  - concept will change
"""

from sstcore.port.color import ColorBox, ColorIdentifier

__all__: list[str] = [
    "ColorBox",
    "NormalizeMixin",
]
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from rich.console import ConsoleRenderable, RichCast

from ....brick.color import colorize
from ....brick.color.box import Colors
from ....port.printer import ColorPrint
from ....port.view import Renderable
from .._base import _BasePrint


class NormalizeMixin(_BasePrint):
    def normalize(self, target: Any) -> Renderable:
        """Normalize targets into renderable representations."""
        match target:  # TASK: find better check for this group
            case ConsoleRenderable() | RichCast() | str() | BaseModel():
                return target
            case list() as items:
                return "\n".join(str(self.normalize(item)) for item in items)
            case Path() as path:
                return colorize.path(path)
            case _:
                return str(target)


class ColorMixin(_BasePrint):
    colors: ColorBox

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors: ColorBox = Colors()

    @property
    def project_info(self) -> str:
        name: str = self.colors.azure(self.info.name)
        return f"{name} v{self.info.version}"

    # NEXT: ArgCast Color?
    def colorize(self, text: str, color: ColorIdentifier) -> str:
        return self.colors(text, color) if text else ""


if TYPE_CHECKING:

    class _Norm(NormalizeMixin, ColorMixin, _BasePrint): ...

    _instance_check: ColorPrint = _Norm()
    _class_check: type[ColorPrint] = _Norm
else:
    from ...brick.none import Ghost

    _Norm = Ghost
