"""
Format and Parse Names in both directions

- NamePattern: pure compilation + core format/extract
- FormatNormalizer: Convert List|Tuple to Dict and sanizize datetime
- ExtractNormalizer: Convert Path to str and sanitze increments
- NameParser: Dispatch input as unified External Access Point 󰣏

Diamond (NameParser -> both normalizers -> NamePattern) works cleanly via MRO.

                                                       DependencyLevel[1]
"""

from sstcore.util.print._mixins import NormalizeMixin

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
from pathlib import Path
from typing import TYPE_CHECKING, Any, overload

# WARN: dependency violation
from ...error import NotImplementedDispatchError
from ..none import Ghost
from ._base import BaseName as _BaseName


class NamePattern(_BaseName):
    """Compile the Pattern, format and parse Keys and Names"""

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

    def normalize_keys(
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
        keys: dict[str, str] = self.normalize_keys(keys)
        return super().format(keys)


class ExtractNormalizer(NamePattern):
    """Extract from String or Path"""

    def normalize_name(self, target: Path | str) -> str:
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
        clean_string: str = self.normalize_name(name)
        return super().extract(clean_string)


if TYPE_CHECKING:

    class _NormalizedName(NormalizeMixin, FormatNormalizer): ...
else:
    _NormalizedName = Ghost


class BidirectionalName(_NormalizedName):
    """Route the Calls trough the right channel"""

    # IDEA: 2 more overload, and then inherit from base???
    @overload
    def __call__(self, target: Path | str) -> dict[str, str]: ...
    @overload
    def __call__(self, target: dict | list | tuple) -> str: ...

    def __call__(self, target: Any):
        """
        Add the bidirectional dispatch

        Send:
        - Path and String to ExtractNormalizer
        - Dict, List and Tuple to FormatNormalizer
        """
        match target:
            case Path() | str():
                return self.extract(target)

            case dict() | list() | tuple():
                return self.format(target)

        raise NotImplementedDispatchError(target)


class NameParser(BidirectionalName, FormatNormalizer, ExtractNormalizer):
    """
    󰣏 Toggle Keyword and String Representation 󰣏

    - Unite the Format and Extract Pipeline
    - Start as new Root for many Parsed Names

    """
