import re
from collections.abc import Callable
from enum import StrEnum
from string.templatelib import Interpolation, Template
from typing import Any

from ....port.calling import Stringable


def normalize(target: Any) -> Stringable:
    return str(target)


def sanitize(template: Template, max_str: int = 120) -> Template:
    def wrap(i: Interpolation) -> Interpolation:
        v = i.value
        if is_sensitive(i.expression):
            v = "***"
        elif isinstance(v, str) and len(v) > max_str:
            v = v[: max_str - 1] + "…"
        return Interpolation(v, i.expression, i.conversion, i.format_spec)

    return map_template(template, wrap)


def map_template(
    template: Template, fn: Callable[[Interpolation], Interpolation]
) -> Template:
    return Template(
        *(fn(p) if isinstance(p, Interpolation) else p for p in template)
    )


def replace_values(template: Template, values: tuple[Any, ...]) -> Template:
    it = iter(values)
    return map_template(
        template,
        lambda i: Interpolation(
            next(it), i.expression, i.conversion, i.format_spec
        ),
    )


class Conversion(StrEnum):
    STRING = "s"
    REPR = "r"
    ASCII = "a"
    NONE = "n"

    @classmethod
    def map(cls, item: str | Interpolation[Any]) -> Stringable:
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


#  LINE: -- Render -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def render(template: Template) -> str:
    return "".join(
        format(item.value, item.format_spec or "")
        if isinstance(item, Interpolation)
        else item
        for item in template
    )


def render_plain(template: Template) -> str:
    parts: list[str] = []
    for item in template:
        if isinstance(item, str):
            parts.append(item)
            continue
        value: Stringable = Conversion.map(item)
        spec: str = item.format_spec
        try:
            parts.append(
                format(value, spec)
                if spec and looks_like_format_spec(spec)
                else str(value)
            )
        except TypeError, ValueError:
            parts.append(str(value))
    return "".join(parts)


#  LINE: -- Checks -- -- - -- -- - -- -- - -- -- - -- -- - -- --

SENSITIVE = (
    "password",
    "passwd",
    "secret",
    "token",
    "key",
    "credential",
)


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
    return bool(spec) and bool(_FORMAT_SPEC_RE.match(spec))


def is_sensitive(expression: str) -> bool:
    lowered = expression.lower()
    return any(part in lowered for part in SENSITIVE)


#  LINE: -- Inspect -- -- - -- -- - -- -- - -- -- - -- -- - -- --


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
