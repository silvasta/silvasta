import re
import time
from collections.abc import Callable, Generator, Iterable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Generic, TypeVar, cast

T = TypeVar("T")


@dataclass(frozen=True)
class MatchRule(Generic[T]):
    """Type-safe definition of a single pattern + what to do when it matches.

    The `action` can be:
      - A static value (e.g. a style string)
      - A callable(text: str, match: re.Match | None) -> T
      - None (falls back to the original text)
    """

    pattern: str
    action: T | Callable[[str, re.Match | None], T] | None = None


class MatchRules(Enum):
    """Base class for rule sets. Subclass this and assign MatchRule instances.

    Example:
        class LogPattern(MatchRules):
            DEBUG = MatchRule(r".*?\bDEBUG\b.*", "bold yellow")
            ...
    """

    def __new__(cls, rule: MatchRule[T]) -> MatchRules:
        # We store the MatchRule directly as the enum value.
        # This gives us full type safety and explicit naming.
        obj = object.__new__(cls)
        obj._value_ = rule
        return obj

    @property
    def rule(self) -> MatchRule[T]:
        return cast(MatchRule[T], self.value)

    @property
    def pattern(self) -> str:
        return self.rule.pattern

    def matches(self, text: str) -> bool:
        """Test whether this rule matches the text."""
        return text == RegexMatch(
            self.pattern
        )  # reuses existing logic + .match side-effect

    def process(self, text: str) -> T | str | None:
        """Execute the configured action or return the static value."""
        rule = self.rule
        match_obj = RegexMatch(rule.pattern).match  # trigger match

        if callable(rule.action):
            return rule.action(text, match_obj)
        return rule.action if rule.action is not None else text


class RegexMatch:
    """Low-level compiled regex with structural pattern matching support.
    Unchanged core, with a small improvement for clarity.
    """

    def __init__(self, pattern: str):
        self.pattern: str = pattern
        self._compiled: re.Pattern[str] = re.compile(pattern)
        self.match: re.Match[str] | None = None

    def __repr__(self) -> str:
        return f"RegexMatch({self.pattern!r})"

    def __hash__(self) -> int:
        return hash(self.pattern)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, str):
            return NotImplemented
        self.match = self._compiled.search(
            other
        )  # Changed to .search (more useful for logs)
        return self.match is not None


class PatternMatcher(Generic[T]):
    """Main exported class.

    Takes a MatchRules subclass and provides a clean, reusable matching pipeline.
    This replaces the ad-hoc match/case + tuple logic everywhere.
    """

    def __init__(self, rules: type[MatchRules], default: T | None = None):
        if not (isinstance(rules, type) and issubclass(rules, MatchRules)):
            raise TypeError("rules must be a subclass of MatchRules")

        self.default: T | None = default
        # Preserve definition order (important for rule precedence)
        self._rules: list[tuple[MatchRules, RegexMatch]] = [
            (member, RegexMatch(member.pattern)) for member in rules
        ]

    def __call__(self, text: str) -> T | str | None:
        """Match text against rules and return the configured action/value."""
        if not isinstance(text, str) or not text.strip():
            return self.default

        for rule_enum, regex in self._rules:
            if text == regex:  # triggers RegexMatch.__eq__ and sets .match
                match_obj = regex.match
                action = rule_enum.rule.action

                if callable(action):
                    return action(text, match_obj)
                return action if action is not None else text

        return self.default

    def process(
        self, lines: Iterable[str]
    ) -> Generator[tuple[str, T | str | None]]:
        """Process multiple lines, returning (cleaned_line, result) pairs."""
        for line in lines:
            if isinstance(line, str) and (cleaned := line.strip()):
                yield cleaned, self(cleaned)

    def tail(
        self, file: Path, sleep: float = 0.1
    ) -> Generator[tuple[str, T | str | None]]:
        """Tail a log file and yield (line, result) for every new line."""
        with open(file, encoding="utf-8") as f:
            f.seek(0, 2)

            while True:
                if not (line := f.readline()):
                    time.sleep(sleep)
                    continue
                if cleaned := line.strip():
                    yield cleaned, self(cleaned)


# Convenient default for logs (kept in this module for now)
class LogPattern(MatchRules):
    """Ready-to-use log level patterns (mainly for loguru output)."""

    DEBUG = MatchRule(r".*?\bDEBUG\b.*", "bold yellow")
    INFO = MatchRule(r".*?\bINFO\b.*", "bold white")
    WARNING = MatchRule(r".*?\bWARNING\b.*", "bold magenta")
    ERROR = MatchRule(r".*?\b(?:ERROR|CRITICAL)\b.*", "bold red")
    SUCCESS = MatchRule(r".*?\bSUCCESS\b.*", "bold green")


# Public API
__all__ = [
    "RegexMatch",
    "MatchRule",
    "MatchRules",
    "PatternMatcher",
    "LogPattern",
]
