"""
Format and Parse Names in both directions

- Build the Engine for specialized tools

"""

import re
import string
from collections.abc import Iterable
from pathlib import Path


class NamePattern:
    """Switch bidirectional between Keywords and String"""

    def __str__(self):
        return f"{type(self).__name__}[:{len(self.keys)}]"

    def __repr__(self):
        return f"{type(self).__name__}[{self.keys}'{self.pattern}']"

    def __rich__(self):
        return f"[cyan]{type(self).__name__}[/][{self.keys}'{self.pattern}']"

    def __init__(self, pattern: str):
        self.pattern: str = pattern
        self.compile_and_set_keys(pattern)

    def format(self, **kwargs) -> str:
        """Create formatted string from keyword arguments"""
        if missing_keys := set(self.keys) - set(kwargs.keys()):
            raise ValueError(f"{self} failed format! {missing_keys=}")
        return self.pattern.format(**kwargs)

    def parse(self, target: Path | str) -> dict[str, str] | None:
        """Parse Name to Keywords and provide Result on Success"""
        formatted: str = target if isinstance(target, str) else target.name
        if match := self._regex.match(formatted):
            return match.groupdict()

    def extract(self, target: Path | str) -> dict[str, str]:
        """Parse Name to Keywords or Raise"""
        if extracted := self.parse(target):
            return extracted
        raise ValueError(f"No match for {self}: {target}")

    def compile_and_set_keys(self, pattern: str):
        """Parse Patten, extract Keys, compile and attach"""
        keys: list[str] = []

        regex_parts: list[str] = ["^"]
        parsed: Iterable = string.Formatter().parse(pattern)
        for literal_text, field_name, _format_spec, _conversion in parsed:
            if literal_text:
                regex_parts.append(re.escape(literal_text))
            if field_name is not None:
                keys.append(field_name)
                regex_parts.append(f"(?P<{field_name}>.+?)")
        regex_parts.append("$")

        self._regex: re.Pattern = re.compile("".join(regex_parts))
        self.keys: tuple[str, ...] = tuple(keys)
