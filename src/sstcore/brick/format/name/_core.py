"""
Format and Parse Names in both directions

- NamePattern: pure compilation + core format/extract

- FormatNormalizer: Convert List|Tuple to Dict and sanitize items
- ExtractNormalizer: Convert Path to str and sanitze increments

- BidirectionalParser: Dispatch input as unified External Access Point 󰣏

- NameParser: Facade and Final Assembly 󰣏

                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "NamePattern",
    "FormatNormalizer",
    "ExtractNormalizer",
    "BidirectionalParser",
    "NameParser",
]

import re
import string
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, overload

from ....error import NotImplementedDispatchError  # WARN: dependency violation

# LATER: decide for: import module or from module import ...
from ....port import normalize
from ....port._link import implements, portlink
from ....port.normalize import (
    Bidirect,
    ExtractNormalizing,
    FormatNormalizing,
    NameParsing,
    NamingPattern,
    OnlyForCheck,
)
from ...none import Ghost
from ._base import BaseName as _BaseName


@portlink(protocol=OnlyForCheck)
class CheckIfTypeCheckingGood:
    def __init__(self):
        self.side_info: dict[str, Any] = {}
        self.other = ...

    @property
    def state(self) -> Any:
        _important = self.side_info.get("whatever", None)
        return self._some_process(_important, self.other)

    def _some_process(self, *args, **kwargs):
        raise NotImplementedError(args, kwargs)

    def handle(self, order: int) -> str:
        """Transform internal state to text depending on order"""
        match order:
            # ... fill here
            case _:
                return str(self.state)


@portlink(protocol=OnlyForCheck)
class CheckIfTypeCheckingMissingSignature:
    def __init__(self):
        self.side_info: dict[str, Any] = {}
        self.other = ...

    @property
    def state(self) -> Any:
        raise NotImplementedError

    def handle(self) -> str:
        """Transform internal state to text depending on order"""
        raise NotImplementedError


@portlink(protocol=OnlyForCheck)
class CheckIfTypeCheckingBadTyping:
    def __init__(self):
        self.side_info: dict[str, Any] = {}
        self.other = ...

    @property
    def state(self) -> Any:
        raise NotImplementedError

    def handle(self, _order: int) -> list[str]:
        """Transform internal state to text depending on order"""
        raise NotImplementedError


if TYPE_CHECKING:
    _pattern: normalize.OnlyForCheck = CheckIfTypeCheckingGood()
    _pattern: normalize.OnlyForCheck = CheckIfTypeCheckingMissingSignature()
    _pattern: normalize.OnlyForCheck = CheckIfTypeCheckingBadTyping()

#  LINE: -- From Here: Official Implementation -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@implements(protocol=NameParsing)
class NamePattern(_BaseName):
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
        self._regex, self.keys = self._compile_pattern(pattern)
        self.pattern = pattern

    def format(self, keys: dict[str, str]) -> str:
        if missing := set(self.keys) - set(keys.keys()):
            raise ValueError(f"{self} Missing keys: {missing}")
        return self.pattern.format(**keys)

    def extract(self, name: str) -> dict[str, str]:
        if match := self._regex.match(name):
            return match.groupdict()
        raise ValueError(f"No match for {self}: {name}")


@implements(protocol=FormatNormalizing)
class FormatNormalizer(NamePattern):
    """Check keys and pre-format datetimes"""

    def normalize_keys(  #  MOVE: to normalize?
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
        keys: dict[str, str] = self.normalize_keys(keys)
        return super().format(keys)


@implements(protocol=ExtractNormalizing)
class ExtractNormalizer(NamePattern):
    def normalize_name(  #  MOVE: to normalize?
        self, target: Path | str
    ) -> str:
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
        clean_string: str = self.normalize_name(name)
        return super().extract(clean_string)


if TYPE_CHECKING:

    class _NormalizedName(ExtractNormalizer, FormatNormalizer): ...
else:
    _NormalizedName = Ghost


@implements(protocol=Bidirect)
class BidirectionalParser(_NormalizedName):
    """Route the Calls trough the right channel"""

    @overload
    def __call__(self, target: Path | str) -> dict[str, str]: ...
    @overload
    def __call__(self, target: dict | list | tuple) -> str: ...

    def __call__(self, target: Any):
        match target:
            case Path() | str():
                return self.extract(target)

            case dict() | list() | tuple():
                return self.format(target)

        # IMPORTANT: replace by FormatError (as soon as this exists) or Raiser!
        raise NotImplementedDispatchError(target)


if TYPE_CHECKING:

    class _BidirectionalName(BidirectionalParser): ...
else:
    # INFO: Re-Ghosting? otherwise ty complains about unstable MRO...
    class _BidirectionalName(
        BidirectionalParser, FormatNormalizer, ExtractNormalizer
    ): ...


@implements(protocol=NamingPattern)
class NameParser(_BidirectionalName):
    """
    󰣏 Toggle Keyword and String Representation 󰣏

    - Unite the Format and Extract Pipeline
    - Start as new Root for many Parsed Names

    """


if TYPE_CHECKING:
    # AI: this is the unchanged usage as before, probably I just keep this at EoF
    _pattern: normalize.NamingPattern = NamePattern("hello {name}")
    _format: normalize.FormatNormalizing = FormatNormalizer("hello {name}")
    _extraat: normalize.ExtractNormalizing = ExtractNormalizer("hello {name}")
    _call: normalize.Bidirect = BidirectionalParser("hello {name}")
    _parser: normalize.NameParsing = NameParser("hello {name}")
