"""
Analyze and Modify ANSI Strings

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "strip",
    "visual_len",
    "truncate",
    #
    "PATTERN",
    "RE",
]

import re

PATTERN = r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"

RE: re.Pattern = re.compile(PATTERN)


def strip(text: str) -> str:
    """Strip ANSI color codes to calculate true visual width."""
    return RE.sub("", text)


def visual_len(text: str) -> int:
    """Return actual display character width ignoring hidden markup."""
    return len(strip(text))


def truncate(text: str, max_width: int, tail: str = "…") -> str:
    """Truncate text to visual width without breaking ANSI escape codes."""

    _visual_len = visual_len(text)

    if _visual_len <= max_width:
        return text

    if _visual_len == len(text):
        return text[: max_width - len(tail)] + tail

    return text[: max_width - len(tail)] + tail
