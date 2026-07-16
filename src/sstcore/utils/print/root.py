"""
Provide Engine for easy access to Rich Console setup

- Load Base with Meta, attach Modus and finally build Core

"""

from collections.abc import Callable
from contextlib import contextmanager

from rich.console import Console
from rich.padding import Padding
from rich.theme import Theme

from ...contract.cli import CliDTO, CliRenderable
from ..color import Palette
from ..color.palette import BASE_PALETTE
from ..view import Cli, Log, Repr, Rich, Str, ViewBuilder, view
from .blueprint import Modus, Printer


@view(ViewBuilder(Cli.BAR, Str.DEFAULT, Rich.SHORT, Repr.DEFAULT, Log.FULL))
class PrinterBase:
    """Provide Base for easy access to Rich Console setup"""

    def __init__(self: Printer, palette: Palette | None = None):
        self.load_theme()
        self.palette: Palette = palette or BASE_PALETTE

    # Inject Name and Version during bootstrap
    project_name: str = "App"
    project_version: str = "0.0.0"

    @property
    def project_info(self) -> str:  # LATER: use ColoredName?
        """Compose Project Meta to show it f.e. in Panel.title"""
        return f"{self.project_name} v{self.project_version}"

    def load_theme(self: Printer, theme: dict[str, str] | None = None):
        """Attach theme to printer and apply to Console"""
        self._rich_theme = Theme(theme or self.palette.to_rich())
        self.console = Console(theme=self._rich_theme)

    def preview_themes(self: Printer):
        """Show all styles of theme in Panel"""
        for style in self._rich_theme.styles.keys():
            text = f" Style Preview: [ {style} ] "
            self.panel(text, frame=style, text_style=style)


class PrinterModi(PrinterBase):
    """Control state of Modus"""

    modus: Modus = Modus.RICH

    def unmute(self):
        """Switch to regular Printer output"""
        self.modus: Modus = Modus.RICH

    def wire(self):
        """Switch to EventBus setup"""
        self.modus: Modus = Modus.EMIT

    def fallback(self):
        """Switch to Python standard print"""
        self.modus: Modus = Modus.PRINT

    def mute(self):
        """Send all prints to nowhere"""
        self.modus: Modus = Modus.NULL

    @contextmanager
    def _in_context(self, strategy: Callable):
        before: Modus = self.modus
        try:
            strategy()
            yield
        finally:
            self.modus: Modus = before

    def unmuted(self):
        return self._in_context(strategy=self.unmute)

    def wired(self):  # WARN: bus must be loaded! or just use global bus?
        return self._in_context(strategy=self.unmute)

    def like_python(self):
        return self._in_context(strategy=self.fallback)

    def muted(self):
        return self._in_context(strategy=self.mute)


class PrinterCore(PrinterModi):
    """Execute the printer()"""

    def __call__(self: Printer, target, **kwargs):
        """Single entry point for all printing logic."""

        # 1. Unpack Renderables (Interfaces)
        if isinstance(target, CliRenderable):
            target = target.__cli__()

        # 2. Route DTOs to RenderMixin, Raw data to NormalizeMixin
        if isinstance(target, CliDTO):
            indent: int = target.indent
            renderable = self.render(target)
        else:
            indent = kwargs.pop("indent", 0)
            renderable = self.normalize(target)

        # 3. Execution
        match self.modus:
            case Modus.PRINT:
                print(renderable)  # Python fallback
            case Modus.NULL:
                pass
            case Modus.EMIT:
                pass
            # event_name = (
            #     f"ui.{dto.__class__.__name__.lower().replace('dto', '')}"
            # )
            # # WARN: no Bus import from Core to Utils!
            # # - maybe use strategy pattern and attach bus function here
            # self.bus.emit(event_name, sender="printer", dto=dto)
            case Modus.RICH:
                if indent and renderable is not None:
                    renderable = Padding(renderable, (0, 0, 0, indent))
                self.console.print(renderable, **kwargs)
