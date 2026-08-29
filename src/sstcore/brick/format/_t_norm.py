import re
from enum import StrEnum
from string.templatelib import Interpolation
from typing import Any

from ...port.view import Stringable

SENSITIVE = ("password", "passwd", "secret", "token", "key", "credential")


_FORMAT_SPEC_RE = re.compile(
    r"""^
    (?:.[<>=^])?      # fill + align
    [-+ ]?            # sign
    \#?
    0?
    \d*
    [_,]?
    (?:\.\d+)?
    [bcdeEfFgGnosxX%]?
    $""",
    re.VERBOSE,
)


def looks_like_format_spec(spec: str) -> bool:
    # AI: why this bool here? just to check if empty/None? (the first)
    return bool(spec) and bool(_FORMAT_SPEC_RE.match(spec))


def is_sensitive(expression: str) -> bool:
    lowered = expression.lower()
    return any(part in lowered for part in SENSITIVE)


def normalize(target: Any) -> Stringable: ...


class Conversion(StrEnum):
    STRING = "s"
    REPR = "r"
    ASCII = "a"
    CLEAN = "c"

    @classmethod
    def _t(cls, item: str | Interpolation[Any]) -> Stringable:
        """Transform t-string"""
        match item:
            case str():
                return Conversion.CLEAN.apply(item)
            case Interpolation():
                target: Stringable = normalize(item.value)
                return cls(value=item.conversion or "c").apply(target)

    def apply(self, target: Stringable) -> Stringable:
        match self.value:
            case "s":
                return str(target)
            case "r":
                return repr(target)
            case "a":
                return ascii(target)
            case "c":
                return target
