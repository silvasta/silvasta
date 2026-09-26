"""
Define the Shape of the Processing Pipelines

- format: raw input -> rich output (not the library)
- norm: fragile input -> stable output
- labor: input and mission -> result

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "NamingPattern",
    "FormatNormalizing",
    "ExtractNormalizing",
    "Bidirect",
    "NameParsing",
]

from datetime import datetime
from pathlib import Path
from typing import Any, Protocol, overload


class NamingPattern(Protocol):
    """Compile the Pattern, format and parse Keys and Names"""

    def format(self, keys: dict[str, str]) -> str:
        """Format string with keywords and pattern"""

    def extract(self, name: str) -> dict[str, str]:
        """Extract keywords from string or Raise"""  # LATER: safe mode with -> None

    def update_pattern(self, pattern: str) -> None:
        """Recompile internal pattern and keywords"""


class FormatNormalizing(NamingPattern, Protocol):
    def normalize_keys(
        self, target: dict[str, str | datetime] | list[Any] | tuple[Any, ...]
    ) -> dict[str, str]:
        """Ensure all keys are present and stringable"""

    def format(self, keys: dict | list | tuple) -> str:
        """Render normalized keywords"""


class ExtractNormalizing(NamingPattern, Protocol):
    def normalize_name(self, target: Path | str) -> str:
        """Ensure stringable name and sanitizing"""

    def extract(self, name: Path | str) -> dict[str, str]:
        """Parse keywords from cleaned string"""


class Bidirect(ExtractNormalizing, FormatNormalizing, Protocol):
    """Route the Calls trough the right channel"""

    @overload
    def __call__(self, target: Path | str) -> dict[str, str]: ...
    @overload
    def __call__(self, target: dict | list | tuple) -> str: ...

    def __call__(self, target: Any):
        """
        Add the bidirectional dispatch

        - Path and String to ExtractNormalizer
        - Dict, List and Tuple to FormatNormalizer
        """


class NameParsing(Bidirect, ExtractNormalizing, FormatNormalizing, Protocol):
    """
    󰣏 Toggle Keyword and String Representation 󰣏

    - Unite the Format and Extract Pipeline
    - Start as new Root for many Parsed Names
    """
