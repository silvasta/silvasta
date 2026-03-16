from rich.console import Console
from rich.markdown import Markdown
from rich.theme import Theme

# NEXT: repair broken title in file-analyzer
# - then attach rich console here
# (or in CLI as it already loads rich)


class Printer:
    def __init__(self):
        self.custom_theme = Theme(
            {
                # TODO: better style and color concept
                # - consider default style in functions below
                "title": "bold white on cyan",
                "info": "black on white",
                "warning": "bold white on yellow",
                "success": "bold white on green",
                "danger": "bold black on red",
            }
        )
        self.console = Console(theme=self.custom_theme)

    def print(self, *args, **kwargs):
        """Regular rich console print"""
        self.console.print(*args, **kwargs)

    def md(self, text, *args, H: int = 0, **kwargs):
        """Generic Markdown printer, first line with section depth H"""

        # Generate Header if argument is set
        if not (0 <= H <= 6):
            fallback_H = 0
            self.console.print(
                f"Markdown Header {H=} invalid (H1 to H6), using {fallback_H=}",
                style="danger",  # Not using self.fail() as this calls self.md() again
            )
            H: int = fallback_H
        prefix: str = f"{'#' * H} " if H > 0 else ""

        # Add default value that gets overridden by key-word argument
        kwargs.setdefault("style", "info")

        self.print(Markdown(f"{prefix}{text}"), *args, **kwargs)

    def title(self, text, *args, **kwargs):
        """Centred H1 title"""
        defaults: dict[str, str] = {
            "style": "title",
            "justify": "center",
        }
        kwargs = defaults | kwargs  # override defaults
        self.md(text, *args, H=1, **kwargs)

    def warn(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "warning",
            "justify": "center",
        }
        kwargs = defaults | kwargs  # override defaults
        self.md(text, *args, H=1, **kwargs)

    def success(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "success",
            "justify": "center",
        }
        kwargs = defaults | kwargs
        self.md(text, *args, H=2, **kwargs)

    def fail(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "danger",
            "justify": "center",
        }
        kwargs = defaults | kwargs
        self.md(text, *args, H=2, **kwargs)

    def _preview_themes(self):
        """Displays all styles in the current theme to visually preview them."""
        self.title("Theme Preview")

        # self.custom_theme.styles contains all registered styles
        for style in self.custom_theme.styles.keys():
            # Print sample text applying the specific style
            self.print(
                f" Style Preview: [ {style} ] ", style=style, justify="center"
            )


printer = Printer()
