"""
Provide Exceptions for sstcore.utils

- PathGuard: Cover all internal Errors and explain with enumerated Reasons

                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "PathGuardError",
    "PathGuardReason",
    #
    # LATER: Candidates:
    # - Printer
    # - NameParser
    # - View
]

from enum import StrEnum
from typing import Any

from ..port.cli import Renderable
from ..utils.color import ColorBox
from ._base import SstError

c: ColorBox = ColorBox.bold()


class PathGuardError(SstError):
    """
    Raise on invalid, existing, not existing and other bad File System States

      - invalid inputs and permission issues
      - existence violations (missing or exists, depending what not is deired)
      - synchronization conflicts

    """

    def __init__(
        self,
        reason: str | PathGuardReason,
        target: Any = None,
        source: Any = None,
        **kwargs: Any,
    ):
        self.reason: str | PathGuardReason = reason
        self.target: Any = target
        self.source: Any = source
        super().__init__(reason, **kwargs)

    @property
    def _short(self):
        return self.reason

    def _modify_scroll(self, lines: list[Renderable]) -> list[Renderable]:
        """Format PathGuard fail for CLI"""
        return [
            lines[0],
            *(f"{c.c('target')}   {self.target}" if self.target else []),
            # NOTE: it will definitely end up in a stringified approach...
            # - all common attributes will be launched by methods
            # - the specific error just picks what he wants: "target", "source"
            # - maybe direct access to tracked class attributes with protocol
            *(f"{c.c('source')}   {self.source}" if self.source else []),
            lines[-1],
        ]


class PathGuardReason(StrEnum):
    """Govern centralized Message distribution for PathGuard failures"""

    NO_INIT = """PathGuard is Not intended as Instance!"""
    INPUT = "PathSpec failed to parse PathInput!"

    MISSING = "Target Missing on Disk!"
    EXISTS = "Target already Exists on Disk!"

    HARDLINK = "Failed to create Hardlink!"
    SYNC = "Transfer refused by SyncMode"

    RELATIVE = "No Relative connection inside FileTree"

    DECORATOR = "Target Invalid for Hybrid-Decorator"
