"""
Provide Engine for easy access to Rich Console setup

- Load Base with Meta, attach Modus and finally build Core

"""

from contextlib import contextmanager

from rich.console import Console, ConsoleRenderable, RichCast
from rich.padding import Padding
from rich.theme import Theme

from ...contract.cli import CliDTO, CliRenderable
from ...contract.external import RenderableType, RichRenderable
from ...contract.log import LogDTO, LogSerializable
from ..color import Palette, colorize
from ..color.palette import BASE_PALETTE
from .blueprint import Modus, Printer


class PrinterMeta:
    """Provide Information and View"""

    project_name: str = "App"
    project_version: str = "0.0.0"

    def set_project_meta(self, name: str = "", version: str = "") -> None:
        """Attach Project specific information for Printer layouts"""
        if name:
            self.project_name: str = name
        if version:
            self.project_version: str = name

    @property
    def project_info(self) -> str:
        """Compose Project Meta to show it f.e. in Panel.title"""
        # LATER: use ColoredName? so far: override in ColorMixin
        # -> ColoredName with auto dispatch str|rich,cli?
        return f"{self.project_name} v{self.project_version}"


class PrinterBase(PrinterMeta):
    """Provide Base with Rich Console and Theme setup"""

    def __init__(self: Printer, palette: Palette | None = None):
        self.palette: Palette = palette or BASE_PALETTE
        self.load_theme()

    def print(self: Printer, *args, **kwargs):
        """Forward directly to Console"""
        # LATER: maybe at least normalize?
        self.console.print(*args, **kwargs)

    def load_theme(self: Printer, theme: dict[str, str] | None = None):
        """Attach theme to printer and apply to Console"""
        self.theme: Theme = Theme(theme) if theme else self.palette.to_rich()
        self.console = Console(theme=self.theme)

        # LATER:
        # printer.load(dict_theme or palette or rich_theme or console)?
        # - check as well ColorBox/Palette, reduce to 1 point

    def preview_themes(self: Printer):
        """Show all styles of rich Theme in Panel"""
        for style in self.theme.styles.keys():
            text = f" Style Preview: [ {style} ] "
            self.panel(text, frame=style, text_style=style)


class PrinterModus(PrinterBase):
    """Control state of Modus"""

    modus: Modus = Modus.RICH

    def mute(self) -> None:
        """Send all prints to nowhere"""
        self.modus: Modus = Modus.NULL

    def debug(self) -> None:
        """Switch to Python standard print"""
        self.modus: Modus = Modus.DEBUG

    def wire(self) -> None:
        """Switch to EventBus setup"""
        # WARN: bus must be loaded, but where? or just use global bus?
        self.modus: Modus = Modus.EMIT

    def unmute(self) -> None:
        """Switch to regular Printer setup"""
        self.modus: Modus = Modus.RICH

    @contextmanager
    def in_modus(self, modus: Modus):
        before: Modus = self.modus
        try:
            self.modus: Modus = modus
            yield
        finally:
            self.modus: Modus = before

    def muted(self):
        return self.in_modus(modus=Modus.NULL)

    def on_debug(self):
        return self.in_modus(modus=Modus.DEBUG)

    def wired(self):
        return self.in_modus(modus=Modus.EMIT)


class PrinterCore(PrinterModus):
    """Execute the printer()"""

    def __call__(self: Printer, target, **kwargs):
        """Single entry point for printing logic"""

        match self.modus:
            case Modus.DEBUG:
                print("Renderable: ", target, "kwargs: ", kwargs)
                return
            # TODO: case PRINT: -> console?
            case Modus.NULL:
                return
            case Modus.EMIT:
                return  # LATER: maybe something, but no circular calls!
            case Modus.RICH:
                pass

        match target:
            case type():
                target: str = colorize.modules(  # MOVE: normalize
                    target,
                    project_color="cyan",
                    module_color="green",
                    target_color="purple",
                )
            case CliRenderable():
                target: CliDTO = target.__cli__()
            case LogSerializable():
                target: LogDTO = target.__log__()

        match target:
            case CliDTO() | LogDTO():
                renderable: RichRenderable = self.render(target)
                print("dto")
            case ConsoleRenderable() | RichCast():
                renderable: RichRenderable = target
            case _:
                # FIX: pydantic goes trough..
                renderable: str = self.normalize(target)

        indent: int = getattr(target, "indent", kwargs.pop("indent", 0))

        i_hope_it_renders: RenderableType = (
            Padding(renderable, (0, 0, 0, indent))
            if indent and renderable is not None
            else renderable
        )

        self.console.print(i_hope_it_renders, **kwargs)
