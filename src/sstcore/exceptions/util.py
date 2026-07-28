"""
Provide Exceptions for sstcore.utils

- PathGuard: Cover all internal Errors and explain with enumerated Reasons
"""

from enum import StrEnum
from typing import Any

from ..contract.cli import Renderable
from ..utils.color import ColorBox
from .base import SstError

# LATER: Candidates:
# - Printer
# - NameParser
# - View

c: ColorBox = ColorBox.bold()


class PathGuardError(SstError):
    """
    Raise on:

      - invalid inputs
      - existence violations (missing or exists, depending what not is deired)
      - permission issues ???
      - synchronization conflicts

    """

    def __init__(
        self,
        reason: str | PathGuardReason,
        target: Any = None,
        source: Any = None,
        catched: Exception | None = None,
        **kwargs: Any,
    ):
        self.reason: str | PathGuardError = reason
        self.target: Any = target
        self.source: Any = source
        self.catched: Exception | None = catched
        super().__init__(reason, **kwargs)

    @property
    def _short(self):
        return self.reason

    def _modify_scroll(self, lines: list[Renderable]) -> list[Renderable]:
        """Format the PathGuard failure for the CLI."""
        if self.catched:
            root_exception_type: str = self._name(self.catched)
            _catched_exception_box = [  # IDEA: Sub-Panel?
                *(f"{c.r(root_exception_type)}  {self.catched}"),
                *(f"{c.g(self.catched)}"),
            ]
        else:
            _catched_exception_box = []
        return [
            lines[0],
            *(f"{c.c('target')}   {self.target}" if self.target else []),
            *(f"{c.c('source')}   {self.source}" if self.source else []),
            *_catched_exception_box,
            lines[-1],
        ]


class PathGuardReason(StrEnum):
    """Govern centralized Message distribution for PathGuard failures"""

    NO_INSTANCE = """PathGuard is Not intended as Instance!"""
    BAD_INPUT = "PathSpec failed to parse PathInput!"

    MISSING = "Target Missing on Disk!"
    EXISTS = "Target already Exists on Disk!"

    HARDLINK = "Failed to create Hardlink!"
    IGNORE = "SyncMode.IGNORE crashes on file exists..."  # REMOVE: later
    SYNC_CONFLICT = "XXX"  # use this insteady of IGNORE

    RELATIVE = "XXJ"

    DECORATOR = "Target Invalid for Hybrid-Decorator"
