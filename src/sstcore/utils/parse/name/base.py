"""
Format and Parse Names in both directions

- NamePattern: pure compilation + core format/extract
- FormatNormalizer: Convert List|Tuple to Dict and sanizize datetime
- ExtractNormalizer: Convert Path to str and sanitze increments
- NameParser: Dispatch input as unified External Acces Point 󰣏

Diamond (NameParser -> both normalizers -> NamePattern) works cleanly via MRO.

"""

__all__: list[str] = [
    "NamePattern",
    "FormatNormalizer",
    "ExtractNormalizer",
    "NameParser",
]

import re
import string
from collections.abc import Iterable
from datetime import datetime
from functools import singledispatchmethod
from pathlib import Path
from typing import Any

from ....exceptions import NotImplementedDispatchError


def _format_brackets(key: str) -> str:  # INFO: don't loose this
    """Needed for proper {key}"""
    return f"{{{key}}}"


class NameBase:
    """Hold Meta and Decoration"""

    pattern: str
    keys: tuple[str, ...]

    @property
    def _name(self):
        return type(self).__name__

    @property
    def _color(self):
        return "cyan"

    def __str__(self):
        return f"{self._name}[:{len(self.keys)}]"

    def __repr__(self):
        return f"{self._name}[{self.keys}'{self.pattern}']"

    def __rich__(self):
        return f"[{self._color}]{self._name}[/][{self.keys}'{self.pattern}']"


class NamePattern(NameBase):
    def __init__(
        self,
        pattern: str,
        strip_extension: bool = False,
        strip_increments: bool = False,
        datetime_format: str = "%Y-%m-%d_%H-%M-%S",
        **_kwargs: Any,
    ) -> None:
        self.update_pattern(pattern)

        # NOTE: not anymore required here -> move at next refactor
        self.strip_extension: bool = strip_extension  # ExtractNormalizer
        self.strip_increments: bool = strip_increments  # ExtractNormalizer
        self.datetime_format: str = datetime_format  # FormatNormalizer

    def _compile_pattern(
        self, pattern: str
    ) -> tuple[re.Pattern, tuple[str, ...]]:
        """Pure function: Parses Pattern, extracts Keys, returns regex and keys."""
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

        return re.compile("".join(regex_parts)), tuple(keys)

    def update_pattern(self, pattern: str) -> None:
        """Mutates state using the pure compiler."""
        self._regex, self.keys = self._compile_pattern(pattern)
        self.pattern = pattern

    def format(self, keys: dict[str, str]) -> str:
        """Format string with keywords and pattern"""
        if missing := set(self.keys) - set(keys.keys()):
            raise ValueError(f"{self} Missing keys: {missing}")
        return self.pattern.format(**keys)

    def extract(self, name: str) -> dict[str, str]:
        """Extract keywords from string or Raise"""  # LATER: safe mode with -> None
        if match := self._regex.match(name):
            return match.groupdict()
        raise ValueError(f"No match for {self}: {name}")


class FormatNormalizer(NamePattern):
    """Check keys and pre-format datetimes"""

    def normalize(
        self, target: dict[str, str | datetime] | list[Any] | tuple[Any, ...]
    ) -> dict[str, str]:
        """Convert datetimes and ensure all keys are present"""

        keys: dict[str, str | datetime] = (
            target
            if isinstance(target, dict)
            else {key: target[i] for i, key in enumerate(self.keys)}
        )
        return {
            key: (
                f"{val:{self.datetime_format}}"
                if isinstance(val, datetime)
                else val  # IDEA: str(val)??
            )
            for key, val in keys.items()
        }

    def format(self, keys: dict | list | tuple) -> str:
        """Render normalized keywords"""
        keys: dict[str, str] = self.normalize(keys)
        return super().format(keys)


class ExtractNormalizer(NamePattern):
    """Extract from String or Path"""

    def normalize(self, target: Path | str) -> str:
        """Normalize type and strip PathGuard increments"""

        name: str = (  # resolve Path to string
            target
            if not isinstance(target, Path)
            else (target.stem if self.strip_extension else target.name)
        )
        return (  # remove Increment *_3.md when flag is set
            name
            if not self.strip_increments
            else re.sub(pattern=r"_\d+(?=\.|$)", repl="", string=name)
        )

    def extract(self, name: Path | str) -> dict[str, str]:
        """Parse keywords from cleaned string"""
        clean_string: str = self.normalize(name)
        return super().extract(clean_string)


# TODO: wire NameBase
# class DispatchName:
#     """ __call__ and distribure """
#     @singledispatchmethod
#     def __call__(self, target: Any):
#         raise NotImplementedDispatchError(target)
#     @__call__.register
#     def _(self, target: Path | str) -> dict[str, Any]:
#         """Send Path and String to ExtractNormalizer"""
#         return self.extract(target)
#     @__call__.register
#     def _(self, target: dict | list | tuple) -> str:
#         """Send Dict, List and Tuple to FormatNormalizer"""
#         return self.format(target)


class NameParser(FormatNormalizer, ExtractNormalizer):  # TODO: DispatchName
    """
    󰣏 Toggle Keyword and String Representation 󰣏

    - Unite the Format and Extract Pipeline
    - Start as new Root for many Parsed Names

    """

    # IDEA: 1 more level: separate __call__! (or Protocol)
    # - why? make FormatNormalizer and ExtractNormalizer replaceable
    #   MRO like: NameParser(NameCall, AnyFormatN, AnyExtractN, NamePattern)
    # - issue: Able to change Format/Extract but attach dispatch?

    @singledispatchmethod
    def __call__(self, target: Any):
        raise NotImplementedDispatchError(target)

    @__call__.register
    def _(self, target: Path | str) -> dict[str, Any]:
        """Send Path and String to ExtractNormalizer"""
        return self.extract(target)

    @__call__.register
    def _(self, target: dict | list | tuple) -> str:
        """Send Dict, List and Tuple to FormatNormalizer"""
        return self.format(target)
