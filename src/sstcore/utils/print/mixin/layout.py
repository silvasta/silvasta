from typing import Any

from rich.markdown import Markdown

from ..base import BasePrinter


class LayoutMixin(BasePrinter):
    """Encapsulate core layout building design blocks"""

    def md(self, text, *args, header: int = 0, **kwargs):
        """Markdown printer, modify first line with header section depth"""

        kwargs.setdefault("style", "info")

        if not (0 <= header <= 6):  # Generate Header if argument is set
            fallback_header = 0
            self(
                f"Markdown Header {header=} invalid (H1 to H6),"
                " using {fallback_header=}",
                style="danger",
            )
            header: int = fallback_header
        prefix: str = f"{'#' * header} " if header > 0 else ""

        self(Markdown(f"{prefix}{text}"), *args, **kwargs)

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def header(
        self, text, text_style: str = "bold white", frame="cyan", **kwargs
    ):
        self.panel(text, text_style=text_style, frame=frame, **kwargs)

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def title(self, text, title="", title_align="right", **kwargs):
        title: str = title or self.name_and_version()
        self.header(text, title=title, title_align=title_align, **kwargs)

    def success(self, text):
        self.header(text, frame="green")

    def danger(self, text):
        self.header(text, frame="red")

    def warn(self, text):
        self.header(text, frame="yellow")

    def special(self, text):
        self.header(text, frame="purple")

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    # TASK: _inverted_theme, test rich reversed but as well,
    # check which theme setups fit together
    # style, header_style = self._match_inverted_style(style)
    def lines(self, lines: list, style="", title: str = "", header: str = ""):
        """Print header as title followed by lines in panel"""
        if header:
            self.header(text=header, frame=style, title=title)
        self.panel(lines, title=title, frame=style, title_align="right")

    def lines_with_len(self, name, lines: list, style: str = "title"):
        header = f"{name}: {len(lines)}"
        self.lines(header=header, title=name, lines=lines, style=style)

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def banner(
        self, target: Any | list[Any], style="cyan", padding=(1, 1), **kwargs
    ):
        self.panel(
            target,
            border_style=f"white on {style}",
            style=style,
            padding=padding,
        )
