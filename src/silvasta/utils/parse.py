import re
from dataclasses import dataclass
from typing import Generator, Iterable


class RegexMatch:
    r"""Store and compare regex pattern, example usage:
    match line:
        case RegexMatch(r".*\[DEBUG\].*") as m:
            print(f"Debug found: {m.match.group(0)}")
    """

    def __init__(self, pattern: str):
        self.pattern: str = pattern
        self._compiled: re.Pattern[str] = re.compile(pattern)  # pre-compile for speed
        self.match: re.Match | None = None

    def __repr__(self):
        return f"RegexMatch(pattern={self.pattern!r})"

    def __hash__(self):
        return hash(self.pattern)

    def __eq__(self, actual):
        if not isinstance(actual, str):
            return False
        self.match: re.Match | None = re.fullmatch(self.pattern, actual)
        return self.match is not None


@dataclass(frozen=True)
class LogPatterns:
    """Centralized log patterns for dot-access in match statements."""

    DEBUG = RegexMatch(r".*\[DEBUG\].*")
    INFO = RegexMatch(r".*\[INFO\].*")
    WARNING = RegexMatch(r".*\[WARNING\].*")
    ERROR = RegexMatch(r".*\[ERROR\].*")
    SUCCESS = RegexMatch(r".*\[SUCCESS\].*")


def grep_from_list(pattern: str, lines: Iterable[str]) -> Generator[str, None, None]:
    """Yield line if it matches the pattern, works with lists or file objects"""

    regex = RegexMatch(pattern)

    for line in lines:
        if line == regex:  # calls stored regex match pattern on line
            yield line


def sanitize(text: str) -> str:
    """Clean text and prepare for further process"""
    # TODO: collect ideas for cleanup with options
    # - remove non-printable chars
    # - create different sets for different purposes
    # -> define later, when known for what to use
    return text.strip()
