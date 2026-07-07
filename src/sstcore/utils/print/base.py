from collections.abc import Callable
from contextlib import contextmanager
from enum import Enum, auto
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from ..color import ColorBox, Palette
from ..color.palette import BASE_PALETTE
from ..log.inspect import debug_log_or_print

# LATER: final split for PrinterMixins, ideas:
# - _debug,_log,_split together with dunders (maybe project) to meta mixin
# - project_name,project_version maybe to new object? (showing DTO render)
# - panel together with other base components (Markdown,Rule) in new mixin
# - header and box derivatives stay as layout


class BasePrinter:
    """Provide Frame for easy access Rich Console setup"""

    _debug: bool = False
    _log: bool = False
    _strict: bool = False

    # Inject Name and Version inside Project bootstrap
    project_name: str = "App"
    project_version: str = "0.0.0"

    @property
    def name_and_version(self) -> str:
        return f"{self.project_name} v{self.project_version}"

    def __init__(self, palette: Palette | None = None):
        self.palette: Palette = palette or BASE_PALETTE
        self.setup_theme()
        self.modus: self.Modus = self.Modus.RICH

    def setup_theme(self, theme: dict[str, str] | None = None):
        self._rich_theme = Theme(theme or self.palette.to_rich_dict())
        self.console = Console(theme=self._rich_theme)

    def preview_themes(self):
        for style in self._rich_theme.styles.keys():
            text = f" Style Preview: [ {style} ] "
            self.panel(text, frame=style, text_style=style)

    @debug_log_or_print(anyway=False)
    def __call__(self, target, **kwargs):
        """Finally Print Target"""

        match self.modus:
            case self.Modus.STANDARD:
                print(self.format(target))
            case self.Modus.NULL:
                pass

            case self.Modus.RICH:  # Engine and Core of printer
                indent: int = kwargs.pop("indent", kwargs.pop("_i", 0))
                _i_hope_it_renders = self.format(target, indent)
                self.console.print(_i_hope_it_renders, **kwargs)

    @debug_log_or_print(anyway=False)
    def panel(self, target: Any, **kwargs) -> None:
        """Provide General Panel Interface and Print prepared Target"""

        # kwargs for panel
        title: str | None = kwargs.pop("title", None)
        text_style: str | None = kwargs.pop("text_style", None)
        frame: str | None = kwargs.pop("frame", None)

        kwargs["border_style"] = frame or "cyan"  # LATER: -> defaults

        # kwargs for __call__
        indent: int = kwargs.pop("indent", kwargs.pop("_i", 0))

        panel_ready_for_execution = Panel(
            renderable=self._panel_target(target, color=text_style),
            title=self._panel_title(title, color="white"),
            **kwargs,
        )
        self(panel_ready_for_execution, indent=indent)

    def _panel_target(self, target: Any, color: str | None = None) -> str:
        """Ensure target is renderable and apply color if provided"""

        if target is None or not (text := self.format(target)):
            return ""  # Safe fallback for Rich renderable

        return self.color(text, color)

    def _panel_title(
        self, title: str | None, color: str | None = None
    ) -> str | None:
        """Ensure title is valid and apply color if provided"""

        if title is None or not (text := self.format(title)):
            return None  # Safe fallback for ignoring title ("" creates hole)

        return self.color(text, color)

    def format(self, target: Any, indent=0) -> Any:
        # LATER: when using protocol, maybe delete this?
        return target

    @property
    def _cb(self) -> ColorBox:
        raise NotImplementedError

    def color(self, text: str, color: str | None) -> str:
        # LATER: when using protocol, maybe delete this?
        return text

    class Modus(Enum):
        RICH = auto()
        STANDARD = auto()
        NULL = auto()

    def mute(self):
        """Send all prints to nowhere"""
        self.modus = self.Modus.NULL

    def unmute(self):
        """Switch to regular Printer output"""
        self.modus = self.Modus.RICH

    def no_fancy(self):
        """Switch to Python standard print"""
        self.modus = self.Modus.STANDARD

    @contextmanager
    def _in_context(self, strategy: Callable):
        modus_before: self.Modus = self.modus
        try:
            strategy()
            yield
        finally:
            self.modus = modus_before

    def muted(self):
        return self._in_context(strategy=self.mute)

    def unmuted(self):
        return self._in_context(strategy=self.unmute)

    def like_python(self):
        return self._in_context(strategy=self.no_fancy)
