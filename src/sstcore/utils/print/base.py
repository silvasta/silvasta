from collections.abc import Callable
from contextlib import contextmanager
from enum import Enum, auto
from typing import Any

from rich import inspect
from rich.console import Console
from rich.control import strip_control_codes  # NEXT:
from rich.panel import Panel
from rich.theme import Theme

from ..color.palette import BASE_PALETTE
from ..log.inspect import debug_log_or_print
from ..parse.rich_str_name import StyledName  # FIX:


# Посмотри, я узнал что это будет полезный!
def test_this_somewhennnn(text: str) -> str:
    """Fix broken or undesired color pattern"""
    inspect(text)  # LATER: inspect rich.inspect
    return strip_control_codes(text)  # NEXT:


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

    def __init__(self):
        self.modus: self.Modus = self.Modus.RICH
        self.setup_theme()

    def setup_theme(self, theme: dict[str, str] | None = None):
        self._rich_theme = Theme(theme or BASE_PALETTE.to_rich_dict())
        self.console = Console(theme=self._rich_theme)

    def preview_themes(self):
        for style in self._rich_theme.styles.keys():
            text = f" Style Preview: [ {style} ] "
            self.panel(text, frame=style, text_style=style)

    @debug_log_or_print(anyway=False)
    def __call__(self, target, **kwargs):
        """Finally Print Target"""

        match self.modus:
            case self.Modus.NULL:
                pass
            case self.Modus.STANDARD:
                print(self.format(target))

            case self.Modus.RICH:  # Engine and Core of all Printers
                indent: int = self._extract_indent(kwargs)  # MOVE: but  where?
                self.console.print(self.format(target, indent), **kwargs)

    def _extract_indent(self, kwargs):  # MOVE: but  where?
        """Filter and Modify kwargs to find indent and ensure Console input"""
        indent: int = kwargs.pop("_i", 0)  # alias as second priority
        return kwargs.pop("indent", 0) or indent

    @debug_log_or_print(anyway=False)
    def panel(
        self, target: Any, title=None, text_style=None, frame=None, **kwargs
    ) -> None:
        """Provide General Panel Interface and Print prepared Target"""
        self(
            Panel(
                renderable=self._prepare(target, color=text_style),
                title=self._prepare(title, color="white"),
                border_style=kwargs.pop("border_style", frame),
                **kwargs,
            )
        )

    def log_plain(self, message: str) -> None:
        # NEXT: check where to appply this
        """Для логов: гарантированно plain-текст, без Rich-тегов."""
        clean = (
            strip_control_codes(message)
            if isinstance(message, str)
            else str(message)
        )
        # Тут можно пробросить в logger.info(clean)
        self._console.print(clean)

    def styled_name(self, sn: StyledName, **values) -> str:
        # NEXT: check where to appply this
        """Удобный хелпер: возвращает Rich-строку или plain,  от флага."""
        if self.use_colors:
            return sn.as_rich(**values)
        return sn.as_str(**values)

    def format(self, target: Any, *args, **kwargs) -> Any:
        """Install Base for FormatMixin"""
        return target

    def color(self, text: str, color: str) -> str:
        """Install Base for ColorMixin"""
        return text

    def _prepare(self, target: Any, color: str | None) -> str:
        """Check Format and Color"""
        if (
            target is None
        ):  # WARN: None needed for empty title, but None fails as target, eg in panel...
            return target
        if not (text := self.format(target)):
            return ""
        if color is None:
            return text
        return self.color(text, color)

    class Modus(Enum):
        RICH = auto()
        STANDARD = auto()
        NULL = auto()

    def mute(self):
        """Send all prints to nowhere"""
        self.modus: self.Modus = self.Modus.NULL

    def unmute(self):
        """Switch to regular Printer output"""
        self.modus: self.Modus = self.Modus.RICH

    def no_fancy(self):
        """Switch to Python standard print"""
        self.modus: self.Modus = self.Modus.STANDARD

    @contextmanager
    def _in_context(self, strategy: Callable):
        modus_before: self.Modus = self.modus
        try:
            strategy()
            yield
        finally:
            self.modus: self.Modus = modus_before

    def muted(self):
        return self._in_context(strategy=self.mute)

    def unmuted(self):
        return self._in_context(strategy=self.unmute)

    def like_python(self):
        return self._in_context(strategy=self.no_fancy)
