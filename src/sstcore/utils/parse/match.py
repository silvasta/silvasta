"""
Compile regex pattern and Match

- RegexMatch: Hash by pattern and hit on equal (target=regex_match)
- LogPatterns: Provide selection of precompiled log pattern

"""

import re
import time
from collections.abc import Generator, Iterable
from dataclasses import dataclass
from pathlib import Path


class RegexMatch:
    r"""
    Compile Regex Pattern and apply it to Equality checks

    Example:
        match line:
            case RegexMatch(r".*\[DEBUG\].*") as m:
                print(f"Debug found: {m.match.group(0)}")
    """

    def __init__(self, pattern: str):
        self.pattern: str = pattern
        # Pre-compile: useful for high-frequency, anyway cheap
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


def yield_from_list(pattern: str, lines: Iterable[str]) -> Generator[str]:
    """Match lines with pattern and yield hits"""
    regex = RegexMatch(pattern)
    for line in lines:
        if line == regex:
            yield line


def tail_log_file(log_file: Path) -> Generator[str]:
    """
    Continuously read end of log file and yield matches with log pattern

    - (intended as example, template and storage...)
    """

    with open(log_file) as file:
        file.seek(0, 2)  # Move to end of file

        while True:
            if not (line := file.readline()):
                time.sleep(0.1)
                continue

            match line:
                case LogPatterns.DEBUG:
                    style: str = "bold yellow"
                case LogPatterns.INFO:
                    style: str = "bold white"
                case LogPatterns.WARNING:
                    style: str = "bold magenta"
                case LogPatterns.ERROR:
                    style: str = "bold red"
                case LogPatterns.SUCCESS:
                    style: str = "bold green"
                case _:
                    style = "dataclass broken..."

            yield style


@dataclass(frozen=True)
class LogPatterns:
    """Provide compiled Log pattern for Match"""

    DEBUG = RegexMatch(r".*DEBUG.*")
    INFO = RegexMatch(r".*INFO.*")
    WARNING = RegexMatch(r".*WARNING.*")
    ERROR = RegexMatch(r".*ERROR.*")
    SUCCESS = RegexMatch(r".*SUCCESS.*")
