"""
Provide Engine for easy access to Rich Console setup

- Load Base with Meta, attach Modus and finally build Core

"""

from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from typing import Any

from ...brick.color.box._colors import Colors
from ...brick.field import RequiredField
from ...port.config import ProjectInformation
from ...port.link import portlink
from ...port.printer import Print, PrinterBase, PrintMode
from ..path import ProjectInfo


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


@portlink(Print)
@portlink(PrinterBase)
class PrinterBase(PrinterModus):
    """Provide Base with Rich Console and Theme setup"""

    info: RequiredField[ProjectInformation] = RequiredField(types=ProjectInfo)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = Colors()

    @property
    def project_info(self) -> str:
        name: str = self.colors.azure(self.info.name)
        # LATER: do this with __str__ or __rich__ for color
        return f"{name} v{self.info.version}"

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
