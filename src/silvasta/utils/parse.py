import re
from collections.abc import Generator, Iterable
from dataclasses import dataclass
from pathlib import Path


class PatternNamer:  # LATER: combine with silvasta.config.Names
    """Factory for bidirectional connection of path and name"""

    # Usage:
    # namer = PatternNamer(config.names.schema_file_pattern)
    # filename = namer.format("robot") # Returns: "robot_schema_columns.csv"
    # extracted = namer.extract(Path("some/dir/robot_schema_columns.csv")) # Returns: "robot"

    # TASK: generalize Pattern Handling!
    # - something like metaclass or some factory for key/pattern pair
    # - create class that holds schema to create instances of pairs:
    # keys: list[str]=[k1,k2,..] and pattern:str=r"what_ever_{k2}_{k1}-bla_{kn}.{k_suffix}"
    # - template string / t"string"?

    def __init__(self, pattern: str):
        self.pattern: str = pattern
        # Simple regex to extract the {name} part dynamically
        # "{name}_schema.csv" -> r"^(.*)_schema\.csv$"
        regex_pattern = pattern.replace("{name}", "(.*)").replace(".", r"\.")
        self._regex = re.compile(f"^{regex_pattern}$")

    def format(self, name: str) -> str:
        """String input -> returns filename string"""
        return self.pattern.format(name=name)

    def extract(self, path: Path) -> str:
        """Path input -> returns extracted name string"""
        match: re.Match[str] | None = self._regex.match(path.name)
        if not match:
            raise ValueError(
                f"Path {path.name} does not match pattern {self.pattern}"
            )
        return match.group(1)


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


def grep_from_list(
    pattern: str, lines: Iterable[str]
) -> Generator[str]:
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
