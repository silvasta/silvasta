from collections.abc import Callable
from contextlib import contextmanager
from enum import Enum, auto
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from ...exceptions.base import NotImplementedMixinError


class BasePrinter:
    """Customized Rich Console setup for easy access"""

    _debug: bool = False

    project_name: str = "App"
    project_version: str = "0.0.0"

    def __init__(self, custom_theme: dict[str, str] | None = None):
        self.modus: self.Modus = self.Modus.RICH
        self.setup_theme(custom_theme)
        self.console = Console(theme=self._rich_theme)

    def __call__(self, *args, **kwargs):
        """Rich console print, printer.mute(): switch to regular print"""

        self.console.print(*args, **kwargs)

    def panel(self, target: Any, **kwargs) -> None:
        if "frame" in kwargs:
            kwargs["border_style"] = kwargs.pop("frame")
        self(Panel(renderable=target, **kwargs))

    def _colorize[T: str | list](self, text: T, style: str) -> T:
        raise NotImplementedMixinError(
            base="BasePrinter",
            mixin=self.__class__.__name__,
            func="_colorize",
        )

    def _format(self, target) -> str:
        raise NotImplementedMixinError(
            base="BasePrinter",
            mixin=self.__class__.__name__,
            func="_format",
        )

    def preview_themes(self):
        """Displays all styles in the current theme to visually preview them."""
        self.panel("Theme Preview")
        for style in self._rich_theme.styles.keys():
            self(f" Style Preview: [ {style} ] ", style=style)

    def setup_theme(self, custom_theme: dict[str, str] | None = None):
        self._raw_theme |= custom_theme or {}
        self._rich_theme = Theme(self._raw_theme)

    # MOVE: maybe to style that provides the default, but for sure attached here
    _raw_theme: dict[str, str] = {
        # LATER: work out nice and efficiant defaults
        "normal": "bold white",
        "info": "black on white",
        "title": "bold white on cyan",
        "warning": "bold black on yellow",
        "success": "bold white on green",
        "danger": "bold black on red",
    }

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

    @contextmanager
    def _in_context(self, strategy: Callable):
        modus_before: self.Modus = self.modus
        try:
            strategy()
            yield
        finally:
            self.modus: self.Modus = modus_before

    def unmuted(self):
        return self._in_context(strategy=self.unmute)

    def muted(self):
        return self._in_context(strategy=self.mute)

    def on_standard_print(self):
        return self._in_context(strategy=self.set_to_standard_print)

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
