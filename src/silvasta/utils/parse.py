import re
import string
from collections.abc import Generator, Iterable
from dataclasses import dataclass
from pathlib import Path


class PatternNamer:
    """Factory for bidirectional connection of filename and keywords"""

    def __init__(self, pattern: str):
        self.pattern: str = pattern
        self.keys: list[str] = []

        # Attach values to self.keys as well
        regex_parts: list[str] = self.create_regex_parts(pattern, self.keys)

        self._regex: re.Pattern = re.compile("".join(regex_parts))

    def __repr__(self):
        return f"{self.pattern} - keys: {self.keys}"

    @staticmethod
    def create_regex_parts(pattern: str, keys: list[str]):
        """Refactor pattern to keys and values"""

        regex_parts: list[str] = ["^"]

        parsed: Iterable = string.Formatter().parse(pattern)

        for literal_text, field_name, _format_spec, _conversion in parsed:
            if literal_text:
                # Add and escape static parts of the string (dots, dashes)
                regex_parts.append(re.escape(literal_text))

            if field_name is not None:
                #  Add dynamic fields as Named Regex Capture Groups: (?P<name>pattern)
                keys.append(field_name)
                # Using .+? (non-greedy) to prevent a greedy match from swallowing separators
                regex_parts.append(f"(?P<{field_name}>.+?)")

        regex_parts.append("$")

        return regex_parts

    def format(self, **kwargs) -> str:
        """Takes keyword arguments and returns the formatted string"""

        if missing := set(self.keys) - set(kwargs.keys()):
            raise ValueError(f"Provide all keys for format! {missing=}")

        return self.pattern.format(**kwargs)

    def extract(self, target: Path | str) -> dict[str, str]:
        """Takes formatted string and returns dict mapping keys to extracted values"""

        formatted_string: str = (
            str(target.name) if isinstance(target, Path) else str(target)
        )

        if match := self._regex.match(formatted_string):
            return match.groupdict()

        raise ValueError(f"No match: {formatted_string=} and {self.pattern=}")


class RegexMatch:
    r"""Store and compare regex pattern. Example usage:
    match line:
        case RegexMatch(r".*\[DEBUG\].*") as m:
            print(f"Debug found: {m.match.group(0)}")
    """

    def __init__(self, pattern: str):
        self.pattern: str = pattern
        # Pre-compile for speed: useful for high-frequency, don't hurt for low-frequency
        self._compiled: re.Pattern[str] = re.compile(pattern)
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


def grep_from_list(pattern: str, lines: Iterable[str]) -> Generator[str]:
    """Yield line if it matches the pattern, works with lists or file objects"""

    regex = RegexMatch(pattern)

    for line in lines:
        if line == regex:  # calls stored regex match pattern on line
            yield line


def sanitize(text: str) -> str:
    """Clean text and prepare for further process"""
    # LATER: collect ideas for cleanup with options
    # - remove non-printable chars
    # - create different sets for different purposes
    # -> define later, when known for what to use
    return text.strip()
