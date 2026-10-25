"""
Provide Engine for easy access to Rich Console setup

- Load Base with Meta, attach Modus and finally build Core

"""

from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from typing import Any

from ...brick import reflect
from ...brick.color.box._colors import Colors
from ...brick.field import RequiredField
from ...port.config import ProjectInformation
from ...port.link import portlink
from ...port.printer import PrintBase, PrintMode
from ..path import ProjectInfo


class PrinterConfiguration:
    """Control PrintMode State"""

    mode: PrintMode = PrintMode.default()  # LATER: PolicyField? MatchField?

    def mute(self) -> None:
        """Send all prints to nowhere"""
        self.modus: PrintMode = PrintMode.NULL

    def unmute(self) -> None:
        """Switch to regular Printer setup"""
        self.modus: PrintMode = PrintMode.default()

    def debug(self) -> None:  # LATER: split PRINT/DEBUG
        """Switch to Python standard print of Args"""
        self.modus: PrintMode = PrintMode.DEBUG

    def muted(self) -> AbstractContextManager:
        return self.in_mode(modus=PrintMode.NULL)

    @contextmanager
    def in_mode(self, modus: PrintMode) -> Generator:
        before: PrintMode = self.modus
        try:
            self.modus: PrintMode = modus
            yield
        finally:
            self.modus: PrintMode = before


@portlink(PrintBase)
class PrinterBase(PrinterConfiguration):
    """Provide Base with Rich Console and Theme setup"""

    info: RequiredField[ProjectInformation] = RequiredField(types=ProjectInfo)

    def __init__(self, **kwargs):
        """Extract and destroy final kwargs"""
        self.colors = Colors()
        if kwargs:
            self(f"{self._cb.r(f'{self}: Undestroyed Kwargs:')} {kwargs!r}")
        super().__init__()

    @property
    def _cb(self) -> Colors:
        return self.colors

    @property
    def project_info(self) -> str:
        return reflect.rich(self.info)

    def __call__(self, target: Any, /, *more, **kwargs):
        """Handle all native Prints"""
        match self.modus:
            case PrintMode.NULL:
                pass
            case PrintMode.PRINT:
                print(target, *more, **kwargs)
            case PrintMode.DEBUG:
                print(f"[DEBUG] target={target!r} more={more} kw={kwargs}")
