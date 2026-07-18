"""
Compile regex pattern and Match

- RegexMatch: Hash by pattern and hit on equal (target=regex_match)
- LogPattern: Provide selection of precompiled log pattern

"""

__all__: list[str] = [
    "RegexMatch",
    "MatchRule",
    "RegexMatchBox",
    "LogMatcher",
    "RuleHandler",
]

import re
import time
from collections.abc import Callable, Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

type RuleHandler[InputT, OutputT] = Callable[[InputT], OutputT]


class _Base:
    pattern: str

    def __str__(self):
        return type(self).__name__

    def __repr__(self):
        return f"{self}[{self.pattern}]"

    def __hash__(self):
        return hash(self.pattern)


class RegexMatch(_Base):
    """Compile Regex Pattern and apply it to Equality checks"""

    def __init__(self, pattern: str):
        self.pattern: str = pattern
        self._compiled: re.Pattern[str] = re.compile(pattern)
        # pre-compile: useful for high-frequency, anyway cheap

    def __call__(self, text: str) -> re.Match | None:
        """Compare compiled pattern with text and return match"""
        return self._compiled.search(text)

    def __eq__(self, text: object) -> bool:
        """Check if text matches the compiled pattern"""
        if not isinstance(text, str):
            return False
        return self(text) is not None


@dataclass(frozen=True)
class MatchRule[ActionArgs: Any, ActionResult: Any]:
    """
    Govern the behaviour of the attached RegexMatch

    On Hit:
      - Return the predefined Value
          or
      - Execute the predefined Function

    """

    pattern: RegexMatch
    func: RuleHandler[ActionArgs, ActionResult]

    def __call__(self, text: ActionArgs) -> ActionResult:
        """Execute task"""
        return self.func(text)

    def fulfills(self, text: ActionArgs) -> bool:
        """Check if text matches internal pattern"""
        return text == self.pattern

    def action(self, text: ActionArgs) -> ActionResult | None:
        """Provide ActionResult if text fulfills internal pattern"""
        if self.fulfills(text):
            return self(text)

    @classmethod
    def compile(cls, pattern: str, func: RuleHandler) -> Self:
        """Create rule that returns static result"""
        return cls(pattern=RegexMatch(pattern), func=func)

    @classmethod
    def simple(cls, pattern: str, value: ActionResult) -> Self:
        """Create rule that returns static result"""
        return cls.compile(pattern=pattern, func=lambda _: value)


@dataclass(frozen=True)
class RegexMatchBox[MatchArgs: Any, MatchResult: Any]:
    """
    Collect MatchRules and provide Interface for Actions

    - stream
    - tail

    """

    # NOTE: consider for loaded functions:
    # args: tuple[Any,...] | None = None
    # kwargs: dict[str,Any] | None = None

    rules: list[MatchRule[MatchArgs, MatchResult]]
    default: MatchRule | None

    def __call__(self, text: MatchArgs) -> MatchResult | None:
        for rule in self.rules:
            if rule.fulfills(text):
                return rule.action(text)
        else:
            if self.default is not None:
                return self.default.action(text)

    def tail(
        self, file: Path, sleep: float = 0.1
    ) -> Generator[tuple[str, MatchResult]]:
        """Yield from tail of file if it matches a Rule"""

        with open(file, encoding="utf-8") as stream_file:
            stream_file.seek(0, 2)  # Move to End of streamed file

            while True:
                if not (line := stream_file.readline().strip()):
                    time.sleep(sleep)
                    continue

                if match := self(line):
                    yield line, match

    @classmethod
    def from_list(
        cls,
        rules: list[MatchRule],
        default: MatchResult | RuleHandler | None = None,
    ) -> Self:
        return cls(rules=rules, default=cls._default_to_rule(default))

    @classmethod
    def _default_to_rule(
        cls,
        default: MatchResult | RuleHandler | None = None,
    ) -> MatchRule[MatchArgs, MatchResult] | None:
        if default is None:
            return None
        if callable(default):
            return MatchRule.compile(pattern="", func=default)
        return MatchRule.simple(pattern="", value=default)

    @classmethod
    def from_table(
        cls,
        data: dict[str, MatchResult | RuleHandler],
        default: MatchResult | RuleHandler | None = None,
    ) -> Self:
        """Init from dict table: { key=pattern : value=task }"""
        return cls(
            rules=[
                MatchRule.compile(pattern=pattern, func=task)
                if callable(task)
                else MatchRule.simple(pattern=pattern, value=task)
                for pattern, task in data.items()
            ],
            default=cls._default_to_rule(default),
        )


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###  Defaults
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

LogMatcher: RegexMatchBox[str, str] = RegexMatchBox.from_list(
    rules=[
        MatchRule.simple(
            pattern=r".*?\bDEBUG\b.*",
            value="bold yellow",
        ),
        MatchRule.simple(
            pattern=r".*?\bINFO\b.*",
            value="bold white",
        ),
        MatchRule.simple(
            pattern=r".*?\bWARNING\b.*",
            value="bold magenta",
        ),
        MatchRule.simple(
            pattern=r".*?\b(?:ERROR|CRITICAL)\b.*",
            value="bold red",
        ),
        MatchRule.simple(
            pattern=r".*?\bSUCCESS\b.*",
            value="bold green",
        ),
    ],
)
