"""
Provide Engine for easy access to Rich Console setup

- Load Base with Meta, attach Modus and finally build Core

"""

from rich.console import Console
from rich.padding import Padding

from ...port.event.dto import CliDTO, EventDTO, LogDTO
from ...port.link import portlink
from ...port.printer import Print, PrintMode
from ...port.represent import CliSerializable, LogSerializable, Richable

# NEXT: from ._layouts import PrinterLayouts


@portlink(Print)
class PrinterCore:  # NEXT: continue MRO here
    """Execute the printer()"""

    def __init__(self, **kwargs):
        self.console = Console()
        super().__init__(**kwargs)

    def __call__(self, target, *more, **kwargs) -> EventDTO:
        # LATER: upgrade the __call__ for multiple targets, *more
        """Single entry point for printing logic"""

        if self.mode != PrintMode.RICH:
            return super.__call__(target, *more, **kwargs)

        if isinstance(target, CliSerializable):
            target: CliDTO = target.__cli__()
        elif isinstance(target, LogSerializable):
            target: LogDTO = target.__log__()

        if isinstance(target, EventDTO):
            renderable: Richable = self.render(target)
        else:
            renderable: Richable = self.render.cli.normalize(target)

        if indent := kwargs.pop("indent", 0):
            renderable = Padding(renderable, (0, 0, 0, indent))

        _i_hope_it_renders = (
            Padding(renderable, (0, 0, 0, indent))
            if (indent := kwargs.pop("indent", 0))
            else renderable
        )
        self.console.print(_i_hope_it_renders, **kwargs)
        return target
