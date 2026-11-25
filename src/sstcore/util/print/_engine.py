"""
Provide Engine for easy access to Rich Console setup

- Load Base with Meta, attach Modus and finally build Core

"""

from typing import overload

from rich.console import Console
from rich.padding import Padding

from ...port.event.dto import CliDTO, EventDTO, LogDTO
from ...port.link import portlink
from ...port.printer import Print, PrintMode
from ...port.represent import CliSerializable, LogSerializable, Richable
from ._layouts import PrinterLayouts


@portlink(Print)
class PrinterCore(PrinterLayouts):
    """Execute the printer()"""

    def __init__(self, **kwargs):
        self.console = Console()
        super().__init__(**kwargs)

    @overload
    def __call__[DTO: EventDTO](self, target: DTO, /, **kwargs) -> DTO: ...
    @overload
    def __call__(
        self, target: object, /, *more: object, **kwargs
    ) -> EventDTO: ...

    def __call__(self, target, /, *more, **kwargs) -> EventDTO:
        # LATER: upgrade the __call__ for multiple targets, *more
        """Single entry point for printing logic"""

        match target:
            case EventDTO() as event_dto:
                if more:
                    event_dto: EventDTO = self.dto.cli(event_dto.content, *more)
            case CliSerializable():
                event_dto: CliDTO = target.__cli__()
            case LogSerializable():
                event_dto: LogDTO = target.__log__()
            case _:
                event_dto: CliDTO = self.dto.cli(target, *more)

        if self.mode != PrintMode.RICH:
            super().__call__(event_dto, **kwargs)
            return event_dto

        renderable: Richable = self.render(event_dto)

        _i_hope_it_renders = (
            Padding(renderable, (0, 0, 0, indent))
            if (indent := kwargs.pop("indent", 0))
            else renderable
        )
        self.console.print(_i_hope_it_renders, **kwargs)
        return target
