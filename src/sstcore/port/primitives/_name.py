"""
Format and Parse Names in both directions

- NamePattern: pure compilation + core format/extract

- FormatNormalizer: Convert List|Tuple to Dict and sanitize items
- ExtractNormalizer: Convert Path to str and sanitze increments

- BidirectionalName: Dispatch input as unified External Access Point 󰣏

- NameParser: Facade and Final Assembly 󰣏

                                  DependencyLevel.sstcore.port[0:3]
"""

# TASK: Parametrization

__all__: list[str] = [
    "NamePattern",
    "FormatNormalizer",
    "ExtractNormalizer",
    "BidirectionalName",
    "NameParser",
]


import re
import string
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any, overload

from .. import normalize
from ._zero import NameView, portlink1

type _Keys = tuple[str, ...]


@portlink1(normalize.NamingPattern)
class NamePattern(NameView):
    def __init__(self, pattern: str, **_kwargs: Any) -> None:
        self.update(pattern)

    def update(self, pattern: str) -> None:
        self._regex, self.keys = self._compile_pattern(pattern)
        self.pattern = pattern

    def _compile_pattern(self, pattern: str, /) -> tuple[re.Pattern, _Keys]:

        keys: list[str] = []
        regex_parts: list[str] = ["^"]
        parsed: Iterable = string.Formatter().parse(pattern)

        for literal_text, field_name, _format_spec, _conversion in parsed:
            # CHECK: formatspec!?
            if literal_text:
                regex_parts.append(re.escape(literal_text))
            if field_name is not None:
                keys.append(field_name)
                regex_parts.append(f"(?P<{field_name}>.+?)")
        regex_parts.append("$")

        return re.compile("".join(regex_parts)), tuple(keys)

    def render(self, keys: dict[str, str]) -> str:
        if missing := set(self.keys) - set(keys.keys()):
            raise ValueError(f"{self} Missing keys: {missing}")
        return self.pattern.format(**keys)

    def extract(self, name: str) -> dict[str, str]:
        if match := self._regex.match(name):
            return match.groupdict()
        raise ValueError(f"No match for {self}: {name}")


@portlink1(normalize.FormatNormalize)
class FormatNormalizer(NamePattern):
    def __init__(
        self,
        pattern: str,
        datetime_format: str = "%Y-%m-%d_%H-%M-%S",
        **kwargs,
    ):
        self.datetime_format: str = datetime_format
        super().__init__(pattern, **kwargs)

    def normalize_keys(
        self, target: dict[str, str | datetime] | list[Any] | tuple[Any, ...]
    ) -> dict[str, str]:
        """Convert datetimes with predefined format"""

        keys: dict[str, str | datetime] = (
            target
            if isinstance(target, dict)
            else {key: target[i] for i, key in enumerate(self.keys)}
        )
        return {
            key: (
                f"{val:{self.datetime_format}}"
                if isinstance(val, datetime)
                # LATER: make this like configurable
                else f"{val.__name__}"
                if isinstance(val, type)
                else val
            )
            for key, val in keys.items()
        }

    def render(self, keys: dict | list | tuple) -> str:
        keys: dict[str, str] = self.normalize_keys(keys)
        return super().render(keys)


@portlink1(normalize.ExtractNormalize)
class ExtractNormalizer(NamePattern):
    def __init__(
        self,
        pattern: str,
        strip_extension: bool = False,
        strip_increments: bool = False,
        **kwargs: Any,
    ):
        self.strip_extension: bool = strip_extension
        self.strip_increments: bool = strip_increments
        super().__init__(pattern, **kwargs)

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
        clean_string: str = self.normalize_name(name)
        return super().extract(clean_string)


@portlink1(normalize.BidirectNaming)
class BidirectionalName(NamePattern):
    """Route the Calls trough the right channel"""

    @overload
    def safe(self, target: Path | str, /) -> dict[str, str] | None: ...
    @overload
    def safe(self, target: dict | list | tuple, /) -> str | None: ...
    def safe(self, target: Any, /) -> dict[str, str] | str | None:
        try:
            return self(target)
        except ValueError, _DispatchTypeError:
            return None

    @overload
    def __call__(self, target: Path | str, /) -> dict[str, str]: ...
    @overload
    def __call__(self, target: dict | list | tuple, /) -> str: ...
    def __call__(self, target: Any, /) -> dict[str, str] | str:
        match target:
            case Path() | str():
                return self.extract(target)
            case dict() | list() | tuple():
                return self.render(target)
        raise _DispatchTypeError(target)


class _DispatchTypeError(TypeError):
    def __init__(self, target: Any, *args: Any, types: tuple[type, ...] = ()):
        self.target = target
        self.available_types: tuple[type, ...] = types
        msg = f"No Dispatch available for {target}[{type(target).__name__}]"
        super().__init__(msg, *(target, *args))


@portlink1(normalize.NameParsing)
class NameParser(BidirectionalName, FormatNormalizer, ExtractNormalizer):
    """
    󰣏 Toggle Keyword and String Representation 󰣏

    - Unite the Format and Extract Pipeline
    - Start as new Root for many Parsed Names
    """
