"""
Provide Engine for easy access to Rich Console setup

- Load Base with Meta, attach Modus and finally build Core

"""

from typing import TYPE_CHECKING

from rich.abc import RichRenderable
from rich.padding import Padding

from ...brick.color import colorize
from ...port.event.dto import CliDTO, LogDTO
from ...port.printer import PrintCore
from ...port.view import CliRenderable, LogSerializable, Renderable


class PrinterCore:
    """Execute the printer()"""

    def __call__(self, target, **kwargs):
        """Single entry point for printing logic"""

        match target:
            case type():
                target: str = colorize.modules(  # MOVE: normalize
                    target,
                    project_color="cyan",
                    module_color="green",
                    target_color="purple",
                )
            case CliRenderable():
                target: CliDTO = target.__cli__()
            case LogSerializable():
                target: LogDTO = target.__log__()

        match target:
            case CliDTO() | LogDTO():
                renderable: Renderable = self.render(target)
            case RichRenderable():  # TEST: maybe remove this rich.abc...
                renderable: RichRenderable = target
            case _:  # FIX: pydantic goes trough..
                renderable: str = self.normalize(target)

        indent: int = getattr(target, "indent", kwargs.pop("indent", 0))

        i_hope_it_renders: Renderable = (
            Padding(renderable, (0, 0, 0, indent))  # ty:ignore
            if indent and renderable is not None
            else renderable
        )

        self.console.print(i_hope_it_renders, **kwargs)


if TYPE_CHECKING:
    _instance: PrintCore = PrinterCore()
    _class: type[PrintCore] = PrinterCore
