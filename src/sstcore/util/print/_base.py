"""
Provide Engine for easy access to Rich Console setup

- Load Base with Meta, attach Modus and finally build Core

"""

from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from typing import TYPE_CHECKING

from rich.console import Console

from ...port.config import ProjectInformation
from ...port.event.dto import CliDTO
from ...port.printer import Print, PrintMode


class PrinterInfo:
    """Collect toml info and show in Panel"""

    info: ProjectInformation

    @property
    def project_info(self) -> str:
        """Override in ColorMixin"""
        return f"{self.info.name} v{self.info.version}"

    def set_info(self, info: ProjectInformation) -> None:
        """Fill at System Bootstrap with info from Config"""
        self.info: ProjectInformation = info


class PrinterModus:
    """Control state of Modus"""

    modus: PrintMode = PrintMode.SST

    def mute(self) -> None:
        """Send all prints to nowhere"""
        self.modus: PrintMode = PrintMode.NULL

    def unmute(self) -> None:
        """Switch to regular Printer setup"""
        self.modus: PrintMode = PrintMode.SST

    def debug(self) -> None:
        """Switch to Python standard print of Args"""
        self.modus: PrintMode = PrintMode.DEBUG

    def muted(self) -> AbstractContextManager[None]:
        return self.in_modus(modus=PrintMode.NULL)

    @contextmanager
    def in_modus(self, modus: PrintMode) -> Iterator[None]:
        before: PrintMode = self.modus
        try:
            self.modus: PrintMode = modus
            yield
        finally:
            self.modus: PrintMode = before


class PrinterBase(PrinterModus, PrinterInfo):
    """Provide Base with Rich Console and Theme setup"""

    def __init__(self):
        self.console = Console()

        # IMPORTANT: forward (or backward) always down to here!!!

    def __call__(self, target: CliDTO, **kwargs) -> CliDTO:
        match self.modus:
            case PrintMode.DEBUG:
                print("Target DTO: ", target, "kwargs: ", kwargs)
                raise NotImplementedError
            case PrintMode.NULL:
                raise NotImplementedError
            case PrintMode.SST:
                self.console.print(target)
                return target


if TYPE_CHECKING:
    _instance: Print = PrinterBase()
    _class: type[Print] = PrinterBase

    class _BasePrint(PrinterBase): ...

else:
    from ...brick.none import Ghost

    _BasePrint = Ghost
