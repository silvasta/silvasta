from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Any

from loguru import logger
from rich.color import Color
from rich.style import Style

type color = str | Color  # color part of style
type Attribute = str | BoxAttribute  # attribute part of style

type style = str | Style  # assembled color and attribute


@dataclass
class Colors:
    black: color = "black"
    red: color = "red"
    green: color = "green"
    yellow: color = "yellow"
    blue: color = "blue"
    magenta: color = "magenta"
    cyan: color = "cyan"
    white: color = "white"


class BoxAttribute(StrEnum):
    NORMAL = auto()
    BOLD = auto()
    INVERT = auto()
    # LATER: check:
    # "frame": "frame",
    # "encircle": "encircle",
    # "overline": "overline",

    def apply_to(self, color: color) -> str:
        attribute: str = {
            self.NORMAL: "",
            self.BOLD: "bold",
            self.INVERT: "reverse",
        }[self]
        return f"{attribute} {color}".strip()


@dataclass
class ColorBox:
    """Isolated string formatter mapping to your core theme definitions."""

    @classmethod
    def with_mode(cls, attribute: str | BoxAttribute = "normal"):
        attribute: str = BoxAttribute(attribute)
        return cls(_attribute=attribute)

    _colors: Colors = field(default_factory=Colors)
    _attribute: BoxAttribute = BoxAttribute.NORMAL

    def set(self, attribute: str | BoxAttribute):
        self._attribute: BoxAttribute = BoxAttribute(attribute)

    def _colorize(self, text: str, color: color) -> str:
        """Main worker that supports all Colors"""

        if style := self._attribute.apply_to(color):
            return f"[{style}]{text}[/]"

        logger.debug("empty call to ColorBox._colorize")  # REMOVE: after tests

        return text

    def white(self, text: Any) -> str:
        return self._colorize(text, self._colors.white)

    def blue(self, text: Any) -> str:
        return self._colorize(text, self._colors.blue)

    def red(self, text: Any) -> str:
        return self._colorize(text, self._colors.red)

    def cyan(self, text: Any) -> str:
        return self._colorize(text, self._colors.cyan)

    def green(self, text: Any) -> str:
        return self._colorize(text, self._colors.green)

    def magenta(self, text: Any) -> str:
        return self._colorize(text, self._colors.magenta)

    def yellow(self, text: Any) -> str:
        return self._colorize(text, self._colors.yellow)

    def black(self, text: Any) -> str:
        return self._colorize(text, self._colors.black)

    def r(self, text: Any) -> str:
        return self._colorize(text, self._colors.red)

    def g(self, text: Any) -> str:
        return self._colorize(text, self._colors.green)

    def b(self, text: Any) -> str:
        return self._colorize(text, self._colors.cyan)


# LATER:
_raw_theme: dict[str, str] = {
    "normal": "bold white",
    "info": "black on white",
    "title": "bold white on cyan",
    "warning": "bold black on yellow",
    "success": "bold white on green",
    "danger": "bold black on red",
}


# LATER:
# REFACTOR: better concept, similar but not the same as rich.reverse
# define pairs of opposite colors that fits well in optic not just reversed
def _match_inverted_style(self, style: str) -> tuple[str, str]:
    if not style:
        return "", ""
    if (header_style := style.lower()) == style:
        return "", style
    if not (line_style := self._inverted_themes.get(header_style)):
        logger.warning(f"No inverted style available: {style=}")
        line_style: str = header_style
    return line_style, header_style


# LATER:
# TASK: define proper pairs
_inverted_themes: dict[str, str] = {
    "info": "white",
    "title": "cyan",
    "warning": "yellow",
    "success": "green",
    "danger": "red",
}
