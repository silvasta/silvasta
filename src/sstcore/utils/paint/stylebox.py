from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Any

from loguru import logger
from rich.color import Color

type color = str | Color  # color part of style
type Attribute = str | BoxAttribute  # attribute part of style


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


BASE_THEME: dict[str, str] = {
    # LATER: iterate over projects, find best common default
    "info": "white",
    "title": "cyan",
    "warning": "yellow",
    "success": "green",
    "danger": "red",
    "special": "purple",
    ### Customized Inverted
    # LATER: use dataclass or other more advanced mechanism
    "Info": "black on white",
    "Title": "bold white on cyan",
    "Warning": "bold black on yellow",
    "Success": "bold white on green",
    "Danger": "bold black on red",
    "Special": "bold white on purple",
}


class BoxAttribute(StrEnum):
    NORMAL = auto()
    BOLD = auto()
    DIM = auto()
    INVERT = auto()
    # LATER: check:
    # "frame": "frame",
    # "encircle": "encircle",
    # "overline": "overline",

    def apply_to(self, color: color) -> str:
        attribute: str = {
            self.NORMAL: "",
            self.BOLD: "bold",
            self.DIM: "dim",
            self.INVERT: "reverse",
        }[self]
        return f"{attribute} {color}".strip()


@dataclass
class ColorBox:
    """Isolated string formatter mapping to your core theme definitions."""

    _log = False

    @classmethod
    def with_mode(cls, attribute: str | BoxAttribute = "normal"):
        attribute: str = BoxAttribute(attribute)
        return cls(_attribute=attribute)

    _colors: Colors = field(default_factory=Colors)
    _attribute: BoxAttribute = BoxAttribute.NORMAL

    def set(self, attribute: str | BoxAttribute):
        self._attribute: BoxAttribute = BoxAttribute(attribute)

    def __call__(self, text: str, color: color) -> str:
        return self._colorize(text, color)

    def _colorize(self, text: str, color: color) -> str:
        """Main worker that supports all Colors"""

        if style := self._attribute.apply_to(color):
            return f"[{style}]{text}[/]"

        if self._log:  # REMOVE: after tests
            logger.debug("empty call to ColorBox._colorize")

        return text

    def white(self, text: Any) -> str:
        return self._colorize(text, self._colors.white)

    def blue(self, text: Any) -> str:
        return self._colorize(text, self._colors.blue)

    def red(self, text: Any) -> str:
        return self._colorize(text, self._colors.red)

    def cyan(self, text: Any) -> str:
        return self._colorize(text, self._colors.cyan)

    def purple(self, text: Any) -> str:
        # LATER: unify Color, BASE_THEME, special somehow
        return self._colorize(text, "purple")

    def green(self, text: Any) -> str:
        return self._colorize(text, self._colors.green)

    def magenta(self, text: Any) -> str:
        return self._colorize(text, self._colors.magenta)

    def yellow(self, text: Any) -> str:
        return self._colorize(text, self._colors.yellow)

    def black(self, text: Any) -> str:
        return self._colorize(text, self._colors.black)

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### Print with short alias (use careful for powerful observable 1-liner)
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    # LATER: final subset of 1char colors

    def r(self, text: Any) -> str:
        return self._colorize(text, self._colors.red)

    def g(self, text: Any) -> str:
        return self._colorize(text, self._colors.green)

    def c(self, text: Any) -> str:
        return self._colorize(text, self._colors.cyan)

    def s(self, text: Any) -> str:
        # LATER: unify Color, BASE_THEME, special somehow
        return self._colorize(text, "purple")

    def y(self, text: Any) -> str:
        return self._colorize(text, self._colors.yellow)
