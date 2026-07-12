"""
Format and Parse Names in both directions

- NameBase: metadata + display
- NamePattern: pure compilation + core format/extract
- FormatNormalizer / ExtractNormalizer: input massaging (different concerns)
- NameParser: unified bidirectional __call__ (the stable root)

Diamond (NameParser -> both normalizers -> NamePattern) works cleanly via MRO.

"""

__all__: list[str] = [
    "NameBase",
    "NamePattern",
    "NameParser",
    "ColoredName",
    "ParsedName",
    "SchemaName",
    "Name",
]

import re
import string
from collections.abc import Iterable
from contextlib import contextmanager
from datetime import datetime
from functools import singledispatchmethod
from pathlib import Path
from typing import Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict, model_validator
from rich.control import strip_control_codes

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
        self.strip_extension: bool = strip_extension
        self.strip_increments: bool = strip_increments
        self.datetime_format: str = datetime_format

        self.update_pattern(pattern)

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

    def format(self, keywords: dict[str, str]) -> str:
        """Format string with keywords and pattern"""
        if missing := set(self.keys) - set(keywords.keys()):
            raise ValueError(f"{self} Missing keys: {missing}")
        return self.pattern.format(**keywords)

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

        keywords: dict[str, str | datetime] = (
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
            for key, val in keywords.items()
        }

    def format(self, keywords: dict | list | tuple) -> str:
        """Render normalized keywords"""
        keywords: dict[str, str] = self.normalize(keywords)
        return super().format(keywords)


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


class NameParser(FormatNormalizer, ExtractNormalizer):
    """
    󰣏 Toggle Keyword and String Representation 󰣏

    - Unite the Format and Extract Pipeline
    - Start as new Root for many Parsed Names

    """

    # WARN: missing __call__ in FormatNormalizer MRO?
    # - at least for the initial idea that ColoredName get no backward parsing
    #   - which in cases makes sense but in general should be no issue
    # I just need to be carfull that no color strings get backward parsed,
    #   and when I see it happens, with this __call__ ... I build a lock

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


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Final Results for Export (in progress...)
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


# Priotity: 4/5
class ColoredName(NameParser):
    """Provide a Colored and a Regular Name with the same Pattern"""

    def __init__(self, pattern: str, **kwargs: Any) -> None:
        self.color_pattern = pattern
        raw_pattern = strip_control_codes(pattern)
        super().__init__(pattern=raw_pattern, **kwargs)

    def update_pattern(self, pattern: str) -> None:
        """Intercept rich pattern, compile both versions."""
        self.color_pattern = pattern
        raw_pattern = strip_control_codes(pattern)
        # We still want regex on the raw pattern for extract()
        super().update_pattern(raw_pattern)

    def rich(self, target: dict | list | tuple) -> str:
        """Colored output using the original rich markup pattern."""
        keywords = self.normalize(target)
        if missing := set(self.keys) - set(keywords.keys()):
            raise ValueError(f"{self} missing keys for rich render: {missing}")
        return self.color_pattern.format(**keywords)

    def raw(self, target: dict | list | tuple) -> str:
        """Explicit raw alias (same as default __call__)."""
        return self.format(target)

    def extract(self, name: Path | str) -> dict[str, Any]:
        """Always extract from the raw (stripped) version."""
        return super().extract(name)  # uses the raw regex

    @contextmanager
    def color_mode(self):
        mode_before: bool = getattr(self, "_color_mode", True)
        self._color_mode = True
        try:
            yield self
        finally:
            self._color_mode: bool = mode_before


class ParsedName[ModelT: BaseModel](NameParser):
    """Switch bidirectional between Keywords and String"""

    model_cls: type[ModelT] | None = None

    def __init__(
        self,
        pattern: str,
        model_cls: type[ModelT] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(pattern=pattern, **kwargs)
        self.model_cls = model_cls

    def extract(self, name: Path | str) -> dict[str, Any] | ModelT:  # ty:ignoer
        raw: dict[str, str] = super().extract(name)  # from ExtractNormalizer
        if self.model_cls is not None:
            return self.model_cls.model_validate(raw)
        return raw


class SchemaName(NameParser, BaseModel):
    """
    Pydantic-native name parser.

    The model fields drive the keys. The class can be used both as
    a validator (TreeNameSchema("t_42_math.json")) and as a parser.

    This is the "melting" version you asked for – it integrates
    cleanly with the existing BaseModel registries in Sachmis.

    Usage in sachmis/config/names.py:

        class TreeNameSchema(SchemaName):
            pattern: ClassVar[str] = "t_{tree_id}_{topic}"
            tree_id: int
            topic: str

        # Then:
        schema = TreeNameSchema.from_name(path)          # explicit
        schema = TreeNameSchema(path)                    # auto via validator
        name_str = schema.to_name()                      # round-trip
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        validate_assignment=True,
        from_attributes=True,
    )

    # Class-level parser cache (one per concrete subclass)
    _parser: ClassVar[NameParser | None] = None

    @model_validator(mode="before")
    @classmethod
    def _parse_name_if_string(cls, data: Any) -> Any:
        if isinstance(data, (str, Path)):
            return cls.from_name(data).model_dump()
        return data

    @classmethod
    def _get_parser(cls) -> NameParser:
        if cls._parser is None and hasattr(cls, "pattern"):
            cls._parser = NameParser(
                pattern=cls.pattern,
                strip_extension=True,
                strip_increments=False,  # important for IDs
            )
        if cls._parser is None:
            raise AttributeError(f"{cls.__name__} has no .pattern")
        return cls._parser

    @classmethod
    def from_name(cls, name: str | Path) -> Self:
        """Primary constructor from filesystem name."""
        parser = cls._get_parser()
        parsed_dict = parser.extract(name)  # uses the raw pipeline
        return cls.model_validate(parsed_dict)

    def to_name(self) -> str:
        """Render back to a filename (raw)."""
        return self._get_parser().format(self.model_dump())

    def __str__(self) -> str:
        return self.to_name()

    def __rich__(self) -> str:
        return f"[cyan]{self.__class__.__name__}[/]: {self.to_name()}"


class Name(NameParser, str):
    """
    Immutable string that knows its own pattern.

    Useful for event names, bus keys, or any place where you want
    a validated string that can still parse itself.

    Example:
        class EventName(Name):
            pattern = "{namespace}.{event}"

        ev = EventName("ui.click")
        data = ev.parse()          # → dict
    """

    def __new__(cls, value: str | Path, **kwargs: Any) -> Self:
        if isinstance(value, Path):
            value = value.name

        parser = NameParser(pattern=getattr(cls, "pattern", value), **kwargs)
        # Validate on construction
        parser.extract(value)

        obj: Self = str.__new__(cls, value)
        obj._parser = parser
        return obj

    def parse(self) -> dict[str, Any]:
        return self._parser.extract(str(self))

    def format(self, **kwargs: Any) -> Name:
        new_value = self._parser.format(kwargs)
        return type(self)(new_value)

    def __rich__(self) -> str:
        return f"[bold cyan]{self}[/]"
