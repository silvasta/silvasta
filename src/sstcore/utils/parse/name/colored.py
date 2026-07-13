from contextlib import contextmanager
from pathlib import Path
from typing import Any

from rich.control import strip_control_codes

from .base import NameParser


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
