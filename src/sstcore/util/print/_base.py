"""
Provide Engine for easy access to Rich Console setup

- Load Base with Meta, attach Modus and finally build Core

"""

from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from typing import Any

from rich.console import Console

from ...brick.field import RequiredField
from ...port.config import ProjectInformation
from ...port.link import portlink
from ...port.printer import Print, PrinterBase, PrintMode
from ..path import ProjectInfo


class PrinterInfo:
    """Collect toml info and show in Panel"""

    info: RequiredField[ProjectInformation] = RequiredField(types=ProjectInfo)
    # CHECK: ProjectInformation=Protocol, ProjectInfo=dataclass, when usw what?

    @property
    def project_info(self) -> str:
        """Override in ColorMixin"""
        return f"{self.info.name} v{self.info.version}"
        # TASK: do this with ProjectInfo.__str__ (.__rich__ for color?)


class PrinterModus:
    """Control state of Modus"""

    mode: PrintMode = PrintMode.default()  # IDEA: PolicyField? MatchField?

    def mute(self) -> None:
        """Send all prints to nowhere"""
        self.modus: PrintMode = PrintMode.NULL

    def unmute(self) -> None:
        """Switch to regular Printer setup"""
        self.modus: PrintMode = PrintMode.default()

    def debug(self) -> None:  # TASK: split PRINT/DEBUG
        """Switch to Python standard print of Args"""
        self.modus: PrintMode = PrintMode.DEBUG

    def muted(self) -> AbstractContextManager[None]:
        return self.in_mode(modus=PrintMode.NULL)

    @contextmanager
    def in_mode(self, modus: PrintMode) -> Generator:
        before: PrintMode = self.modus
        try:
            self.modus: PrintMode = modus
            yield
        finally:
            self.modus: PrintMode = before


# NEXT: Figure out proper base


@portlink(Print)
@portlink(PrinterBase)
class PrinterBase(PrinterModus, PrinterInfo):
    """Provide Base with Rich Console and Theme setup"""

    def __init__(self):
        self.console = Console()

    def __call__(self, target: Any, *more, **kwargs) -> None:
        match self.modus:
            case PrintMode.NULL:
                return
            case PrintMode.PRINT:
                print(target, *more, **kwargs)
                return
            case PrintMode.DEBUG:
                print("Target: ", target, "More: ", more, "kwargs: ", kwargs)
                raise NotImplementedError
