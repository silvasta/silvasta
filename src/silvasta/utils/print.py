from loguru import logger
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme

from .path import pyproject_name


class Printer:
    """Customized Rich Console setup for easy acces"""

    _raw_theme: dict[str, str] = {
        "info": "black on white",
        "normal": "white on black",
        "title": "bold white on cyan",
        "warning": "bold white on yellow",
        "success": "bold white on green",
        "danger": "bold black on red",  # Idea: "danger3": "bold red on black",
    }
    _fallback_to_standard_print = False

    def __init__(
        self,
        custom_theme: dict[str, str] | None = None,
        name: str | None = None,
    ):
        self.update_theme_load_console(custom_theme)
        self.set_project_name(name)

    def __call__(self, *args, **kwargs):
        """Rich console print, printer.mute(): swich to regular print"""
        if self._fallback_to_standard_print:
            print(args[0] or "Something went wrong in defaulting: printer()")
        else:
            self.console.print(*args, **kwargs)

    def mute(self):
        """Swich to regular Python print"""
        self._fallback_to_standard_print = True

    def unmute(self):
        """Swich to Rich console print"""
        self._fallback_to_standard_print = False

    def md(self, text, *args, header: int = 0, **kwargs):
        """Markdown printer, modify first line with header section depth"""

        if not (0 <= header <= 6):  # Generate Header if argument is set
            fallback_header = 0
            self(
                f"Markdown Header {header=} invalid (H1 to H6), using {fallback_header=}",
                style="danger",
            )
            header: int = fallback_header
        prefix: str = f"{'#' * header} " if header > 0 else ""

        kwargs.setdefault("style", "info")

        self(Markdown(f"{prefix}{text}"), *args, **kwargs)

    def panel(self, text: str, title=None, title_align="right", style="info"):
        self(
            Panel(
                renderable=text,
                title=title or self.project_name,
                title_align=title_align,
                style=style,
            )
        )

    def title(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "title",
            # "justify": "center", # INFO: no longer possible/needed after swich from Markdown to Panel
        }
        kwargs = defaults | kwargs  # override defaults
        self.panel(text, *args, **kwargs)

    # TODO: check defaults, check again Markdown H=1 as title

    def warn(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "warning",
            # "justify": "center", # INFO: no longer possible/needed after swich from Markdown to Panel
        }
        kwargs = defaults | kwargs  # override defaults
        self.panel(text, *args, **kwargs)

    def success(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "success",
            # "justify": "center", # INFO: no longer possible/needed after swich from Markdown to Panel
        }
        kwargs = defaults | kwargs
        self.panel(text, *args, **kwargs)

    def fail(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "danger",
            # "justify": "center", # INFO: no longer possible/needed after swich from Markdown to Panel
        }
        kwargs = defaults | kwargs
        self.panel(text, *args, **kwargs)

    def update_theme_load_console(
        self, custom_theme: dict[str, str] | None = None
    ):
        """Override current theme with custom_theme and attach to console"""
        if custom_theme:
            self._raw_theme |= custom_theme

        self._rich_theme = Theme(self._raw_theme)
        self.console = Console(theme=self._rich_theme)

    def preview_themes(self):
        """Displays all styles in the current theme to visually preview them."""

        self.title("Theme Preview")
        for style in self._rich_theme.styles.keys():
            self(f" Style Preview: [ {style} ] ", style=style, justify="center")

    def set_project_name(self, name: str | None = None):
        try:
            self.project_name: str = pyproject_name()
        except FileNotFoundError:
            logger.warning("No pyproject.toml found to set project_name")
            self.project_name: str = "ModifyConfigDefaults"  # TODO: add this to config.settings.defaults


printer = Printer()
