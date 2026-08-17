"""
Provide basic Toolkit for Text formatting

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "strip_ansi",
    "visual_len",
    "truncate",
    # case
    "to_snake",
    "to_camel",
    "to_pascal",
    "to_kebab",
    # align
    "indent",
    "pad",
]

import re

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### ANSI
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


_ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    """Strip ANSI color codes to calculate true visual width."""
    return _ANSI_RE.sub("", text)


def visual_len(text: str) -> int:
    """Return actual display character width ignoring hidden markup."""
    return len(strip_ansi(text))


def truncate(text: str, max_width: int, tail: str = "…") -> str:
    """Truncate text to visual width without breaking ANSI escape codes."""
    if visual_len(text) <= max_width:
        return text

    # Simple visual truncation for plain/light strings
    plain = strip_ansi(text)
    if len(plain) == len(text):
        return text[: max_width - len(tail)] + tail

    # Handles raw strings safely
    return text[: max_width - len(tail)] + tail


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Case
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def to_snake(text: str) -> str:
    s: str = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower().replace("-", "_")


def to_camel(text: str) -> str:
    components = to_snake(text).split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def to_pascal(text: str) -> str:
    return "".join(x.title() for x in to_snake(text).split("_"))


def to_kebab(text: str) -> str:
    return to_snake(text).replace("_", "-")


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Align
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def indent(
    text: str, prefix: str = "  ", first_line_prefix: str | None = None
) -> str:
    """Indent lines cleanly, with optional distinct prefix for the first line."""
    lines = text.splitlines()
    if not lines:
        return ""

    first = (
        first_line_prefix if first_line_prefix is not None else prefix
    ) + lines[0]
    rest = [f"{prefix}{line}" if line.strip() else line for line in lines[1:]]
    return "\n".join([first] + rest)


def pad(
    text: str, width: int, align: str = "left", fillchar: str = " "
) -> str:
    """Align text visually based on strip_ansi width."""
    vlen = visual_len(text)
    if vlen >= width:
        return text

    missing = width - vlen
    if align == "left":
        return text + (fillchar * missing)
    elif align == "right":
        return (fillchar * missing) + text
    elif align == "center":
        left = missing // 2
        right = missing - left
        return (fillchar * left) + text + (fillchar * right)
    return text
