import sys
from collections.abc import Callable
from contextlib import contextmanager
from enum import Enum, auto
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from ...exceptions.base import NotImplementedMixinError
from ..log.inspect import debug_log_or_print


class BasePrinter:
    """Customized Rich Console setup for easy access"""

    _debug: bool = False
    _log: bool = False

    # Fill in Project with import and inject
    project_name: str = "App"
    project_version: str = "0.0.0"

    def __init__(self, custom_theme: dict[str, str] | None = None):
        self.modus: self.Modus = self.Modus.RICH
        self.setup_theme(custom_theme)
        self.console = Console(theme=self._rich_theme)

    @debug_log_or_print(anyway=False)
    def __call__(self, *args, **kwargs):
        """Finally, send the prepared targets trough rich.Console."""

        # The Core of all Printers
        self.console.print(*args, **kwargs)

    @debug_log_or_print(anyway=False)
    def panel(self, target: Any, **kwargs) -> None:
        """Provide interface for rich.Panel pipeline"""
        self(Panel(renderable=target, **kwargs))

    def _colorize[T: str | list](self, text: T, style: str) -> T:
        raise NotImplementedMixinError(
            base=b[0].__name__
            if (b := type(self).__bases__)
            else "BasePrinter",
            mixin=type(self).__name__,
            func=sys._getframe().f_code.co_name,
        )

    def _format(self, target) -> str:
        raise NotImplementedMixinError(
            base=b[0].__name__
            if (b := type(self).__bases__)
            else "BasePrinter",
            mixin=type(self).__name__,
            func=sys._getframe().f_code.co_name,
        )

    def preview_themes(self):
        """Displays all styles in the current theme"""
        self.panel("Theme Preview")  # LATER: update a bit
        for style in self._rich_theme.styles.keys():
            self(f" Style Preview: [ {style} ] ", style=style)

    def setup_theme(self, custom_theme: dict[str, str] | None = None):
        self._raw_theme |= custom_theme or {}
        self._rich_theme = Theme(self._raw_theme)

    _raw_theme: dict[str, str] = {  # LATER: find nice and consistent defaults
        # MOVE: maybe to style that provides default,
        # - but for sure attached here
        "normal": "white",
        "info": "white",
        "title": "cyan",
        "warning": "yellow",
        "success": "green",
        "danger": "red",
        ### ---
        "Normal": "bold white",
        "Info": "black on white",
        "Title": "bold white on cyan",
        "Warning": "bold black on yellow",
        "Success": "bold white on green",
        "Danger": "bold black on red",
    }

    def name_and_version(self) -> str:
        parts: list[str] = []
        if self.project_name:
            parts.append(self.project_name)
        if self.project_version:
            if self.project_version.startswith("v"):
                parts.append(self.project_version)
            else:
                parts.append(f"v{self.project_version}")
        return " ".join(parts) if parts else ""

    class Modus(Enum):
        RICH = auto()
        STANDARD = auto()
        NULL = auto()

    def mute(self):
        """Send all prints to nowhere"""
        self.modus: self.Modus = self.Modus.NULL

    def unmute(self):
        """Switch to Rich Console Printer"""
        self.modus: self.Modus = self.Modus.RICH

    def set_to_standard_print(self):
        """Switch to standard Python print"""
        self.modus: self.Modus = self.Modus.STANDARD

    def unmuted(self):
        return self._in_context(strategy=self.unmute)

    def muted(self):
        return self._in_context(strategy=self.mute)

    def on_standard_print(self):
        return self._in_context(strategy=self.set_to_standard_print)

    @contextmanager
    def _in_context(self, strategy: Callable):
        modus_before: self.Modus = self.modus
        try:
            strategy()
            yield
        finally:
            self.modus: self.Modus = modus_before
