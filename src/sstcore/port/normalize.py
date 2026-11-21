"""
Define the Shape of the Processing Pipelines

- format: raw input -> rich output (not the library)
- norm: fragile input -> stable output
- labor: input and mission -> result

                                    DependencyLevel.sstcore.port[0]
"""  # TODO: out-outdated...

__all__: list[str] = [
    "NamingPattern",
    "FormatNormalize",
    "ExtractNormalize",
    "BidirectNaming",
    "NameParsing",
]

from datetime import datetime
from pathlib import Path
from typing import Any, Protocol, overload
from typing import runtime_checkable as _runtime_checkable

from ._types import _Stringable

#  LINE: -- Definitions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@_runtime_checkable  # LATER: check where used/needed
class Normalizing(Protocol):
    def __call__(self, text: Any) -> _Stringable:
        """Forward text-like object after processing and ensuring string"""


@_runtime_checkable  # LATER: check where used/needed
class Sanitize[ExpectedT, UnexpectedT, TargeT](Protocol):
    def __call__(self, target: ExpectedT | UnexpectedT) -> TargeT:
        """Forward object after processing and ensuring types"""


@_runtime_checkable  # LATER: check where used/needed
class NormalizingMaybe[ExpectedT: _Stringable](
    Sanitize[ExpectedT, Any, _Stringable], Protocol
):
    """Forward text after processing and ensuring string(able)"""


#  LINE: -- ParsedName Normalizing Pipeline -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# TASK: Parametrization


class NamingPattern(Protocol):
    """Compile the Pattern, format and parse Keys and Names"""

    def render(self, keys: dict[str, str]) -> str:
        """Format string with keywords and pattern"""

    def extract(self, name: str) -> dict[str, str]:
        # LATER: safe mode with -> None ?
        # (current safe mode is with (avoidable) catch)
        """Extract keywords from string or Raise"""

    def update(self, pattern: str) -> None:
        """Recompile internal pattern and keywords"""


class FormatNormalize(Protocol):
    def normalize_keys(  # LATER: remove? implementation detail
        self, target: dict[str, str | datetime] | list[Any] | tuple[Any, ...]
    ) -> dict[str, str]:
        """Ensure all keys are present and stringable"""

    def render(self, keys: dict | list | tuple) -> str:
        """Render normalized keywords"""


class ExtractNormalize(Protocol):
    def normalize_name(self, target: Path | str) -> str:  # LATER: remove?
        """Ensure stringable name and sanitizing"""

    def extract(self, name: Path | str) -> dict[str, str]:
        """Parse keywords from cleaned string"""


class BidirectNaming(Protocol):
    """Route the Calls trough the right channel"""

    @overload
    def safe(self, target: Path | str, /) -> dict[str, str] | None: ...
    @overload
    def safe(self, target: dict | list | tuple, /) -> str | None: ...
    def safe(self, target: Any, /) -> dict[str, str] | str | None:
        """Gatekeeper for Error that returns None for bad Parsings"""

    @overload
    def __call__(self, target: Path | str, /) -> dict[str, str]: ...
    @overload
    def __call__(self, target: dict | list | tuple, /) -> str: ...
    def __call__(self, target: Any, /):
        """
        Add the bidirectional dispatch

        - Path and String to ExtractNormalizer
        - Dict, List and Tuple to FormatNormalizer
        """


class NameParsing(BidirectNaming, ExtractNormalize, FormatNormalize, Protocol):
    """
    󰣏 Toggle Keyword and String Representation 󰣏

    - Unite the Format and Extract Pipeline
    - Start as new Root for many Parsed Names
    """
