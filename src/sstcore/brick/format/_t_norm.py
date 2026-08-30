import re
from enum import StrEnum
from string import Template
from string.templatelib import Interpolation
from typing import Any

from ...port.view import Stringable


def render(template: Template) -> str:
    return "".join(
        format(item.value, item.format_spec or "")
        if isinstance(item, Interpolation)
        else item
        for item in template
    )


def resolve(self, obj_type: type) -> ViewFn | None:
    for cls in obj_type.__mro__:
        if cls in self._exact:
            return self._exact[cls]
    return None


class Conversion(StrEnum):
    STRING = "s"
    REPR = "r"
    ASCII = "a"
    NONE = "n"

    @classmethod
    def _t(cls, item: str | Interpolation[Any]) -> Stringable:
        """Transform t-string"""
        match item:
            case str():
                return Conversion.NONE.apply(item)
            case Interpolation():
                target: Stringable = normalize(item.value)
                return cls(value=item.conversion or "n").apply(target)

    def apply(self, target: Stringable) -> Stringable:
        match self.value:
            case "s":
                return str(target)
            case "r":
                return repr(target)
            case "a":
                return ascii(target)
            case "n":
                return target


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


def inspect_template(template: Template) -> Any:
    print("--- Start ---")
    print(template)
    for item in template:
        if isinstance(item, Interpolation):
            print("Interpolation: ", item)
            inspect_values(template.values)
        else:
            print("No interpolation: ", item)
    print("--- End ---")


def inspect_values(values: tuple[Any]):
    for value in values:
        prints = (f"str: {value}", f"type:{type(value).__name__}", f"{value=}")
        print("".join(f"\n   {p}" for p in prints))
