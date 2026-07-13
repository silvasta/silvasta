"""
Compile regex pattern and Match

- RegexMatch: Hash by pattern and hit on equal (target=regex_match)
- LogPatterns: Provide selection of precompiled log pattern

"""

import re
import time
from collections.abc import Generator, Iterable
from enum import StrEnum
from pathlib import Path
from typing import Any

__all__: list[str] = [
    "RegexMatch",
    "MatchRules",
    "LogPattern",
    "RegexMatchBox",
]


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
            return False  # Error?
        self.match: re.Match | None = re.fullmatch(self.pattern, actual)
        return self.match is not None


class MatchRules(StrEnum):
    """
    Govern the behaviour of attached RegexMatches

    - Return their predefined Value
    or
    - Execute their predefined Function

    TODO: something else?
    """

    _regex: re.Pattern  # WARN: problems with Enum?
    result: Any  # WARN: problems with Enum?

    def __new__(cls, pattern: str, result: Any = None):
        # Store pattern as the string value of the enum member
        obj = str.__new__(cls, pattern)
        obj._value_ = pattern
        obj.pattern = pattern
        obj.result = result
        obj._regex = RegexMatch(pattern)
        return obj

    def matches(self, text: str) -> bool:
        # REMOVE: when is this ever needed??
        # IDEA: this -> __eq__ ?
        """Test if this pattern matches the text."""
        return text == self._regex

    def process(self, text: str) -> Any:
        # REMOVE: when is this ever needed??
        """Return configured result or call handler if result is callable."""
        if callable(self.result):
            # Pass both text and the match object (with captured groups)
            return self.result(text, self._regex.match)
        return self.result if self.result is not None else text


class LogPattern(MatchRules):
    # TODO: default RegexMatchBox with this?
    # - this is actually frequetly used in the Bus, Cli or Tui
    """Provide MatchRules log defaults, mainly targeting loguru"""

    # ISSUE: tuple assign is compact, and it needs to be done only once
    # - still the maintainability and comfort decay to zero
    # - Requirement: type safe and hard hard to fail, both violated!
    # TASK: work out better concept:
    # Idea 1, define MatchRules.action that returns a value or calls function
    # Idea 2, create Functor dataclass, equiped with every meta needed,
    # - like pattern, value|function and all potential args for this
    # - pro: bundled compact setup, hard to fail, easily changed if needed
    # - con: annoying assignment for simple pattern:str,value:str
    # Idea 3: Base: split -> static return, or -> dynamic execution
    DEBUG = (r".*?\bDEBUG\b.*", "bold yellow")
    INFO = (r".*?\bINFO\b.*", "bold white")
    WARNING = (r".*?\bWARNING\b.*", "bold magenta")
    ERROR = (r".*?\b(?:ERROR|CRITICAL)\b.*", "bold red")
    SUCCESS = (r".*?\bSUCCESS\b.*", "bold green")


class RegexMatchBox:  # TODO: initial T was bad, but ExplainedT with properly declaring useage?
    """
    Collect MatchRuleSet and provide Interface for Actions

    - Compare incoming string with assigned Rules
    - On hit:
      - provide predefined value
        or
      - execute assigned function

    """

    def __init__(self, core: type[MatchRules], default: Any = None):
        if not (issubclass(core, MatchRules)):
            raise TypeError("pattern_enum must be a subclass of MatchPattern")
        self.default: Any = default
        # NEXT:
        self._routes = [
            # ISSUE: List of tuples? Fail! Use the Enum for that!!!!!
            (re.compile(member.value[0]), member.value[1])
            for member in core
        ]

    def __call__(self, text: str) -> Any:
        """Match string for Result or get default?"""
        if not text or not isinstance(text, str):
            return self.default  # default for wrong type?

        for pattern, action in self._routes:
            if match := pattern.search(text):
                # ISSUE: does not fulfill architectural requirements!
                # Beside this ty: │   │    info: Attempted to call intersection type `str & Top[(...) -> object]` ty (call-top-callable) [128, 24]
                # I don't wire up an ultra safe Enum setup... to rely on tuple decomposition!
                return action(text, match) if callable(action) else action

    def process(self, lines: Iterable[str]) -> Generator[Any]:
        for line in lines:
            # NOTE: check if check here makes sense, or better centralized at 1 place
            if isinstance(line, str) and (cleaned := line.strip()):
                yield cleaned, self(cleaned)

    def tail(
        self, file: Path, sleep: float = 0.1
    ) -> Generator[Any]:  # TODO: here something with T???
        # IDEA: [ActionResultType: None] ?? yes it is long but it 100% describes the purpose
        """Process tail of stream_file and execute Action defined in Enum"""

        with open(file, encoding="utf-8") as stream_file:
            stream_file.seek(0, 2)  # Move to End of streamed file

            while True:
                if not (line := stream_file.readline()):
                    time.sleep(sleep)
                    continue

                if cleaned := line.strip():
                    yield cleaned, self(cleaned)
