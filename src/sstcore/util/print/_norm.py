"""
Ensure pipeline arguments

- normalize: from Any type to stable string
- colorize: attach color and color combinations

Note:
  - still under construction
  - concept will change
"""

__all__: list[str] = [
    "NormalizeMixin",
]
from pathlib import Path
from typing import Any

from rich.console import ConsoleRenderable, RichCast

from ...brick.color import colorize
from ...port.represent import CliRenderable, PydanticModel


class NormalizeMixin:
    def normalize(self, target: Any) -> CliRenderable:  # NEXT: CliRenderable??
        """Normalize targets into renderable representations."""
        match target:  # TASK: find better check for this group
            case ConsoleRenderable() | RichCast() | str() | PydanticModel():
                return target
            case list() as items:
                return "\n".join(str(self.normalize(item)) for item in items)
            case Path() as path:
                return colorize.path(path)
            case _:
                return str(target)
