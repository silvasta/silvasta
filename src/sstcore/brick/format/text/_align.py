"""
Modify the Position of the Text inside a String

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "indent",
    "pad",
]

from ._ansi import visual_len


def indent(
    text: str, prefix: str = "  ", first_line_prefix: str | None = None
) -> str:
    """Indent lines cleanly, with optional distinct prefix for the first line."""
    if not (lines := text.splitlines()):
        return ""
    first: str = (
        first_line_prefix if first_line_prefix is not None else prefix
    ) + lines[0]

    rest: list[str] = [
        f"{prefix}{line}" if line.strip() else line for line in lines[1:]
    ]
    return "\n".join([first] + rest)


def pad(
    text: str, width: int, align: str = "left", fillchar: str = " "
) -> str:
    """Align text visually based on strip_ansi width."""
    vlen = visual_len(text)
    if vlen >= width:
        return text

    missing = width - vlen
    # TODO: Enum, make machine out of this!
    if align == "left":
        return text + (fillchar * missing)
    elif align == "right":
        return (fillchar * missing) + text
    elif align == "center":
        left = missing // 2
        right = missing - left
        return (fillchar * left) + text + (fillchar * right)
    return text
