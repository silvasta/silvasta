import re
from contextlib import contextmanager
from typing import Self

from pydantic import PrivateAttr

from .parsed_name import ParsedName
from .regex import PatternNamer


class StyledName(ParsedName):  # TASK: adapt to new ParsedName
    style_pattern: str
    styles: list[str]

    _styler: PatternNamer | None = PrivateAttr(default=None)
    _styled: bool = PrivateAttr(default=False)

    def _sync_styler_and_styles(self):
        """Runs automatically whenever the model is instantiated or updated."""
        rich_template: str = self.style_pattern

        for i, style in enumerate(self.styles, start=1):
            rich_template: str = rich_template.replace(f"{{style{i}}}", style)

        self._styler = PatternNamer(rich_template)

    def _forward_parsing(self, clean_target: dict[str, str]) -> str:
        """Used for override and intercept in StyledName"""

        if self._styled:
            if self._styler is None:
                self._sync_styler_and_styles()

            if self._styler is not None:
                return self._styler.format(**clean_target)

        return self._namer.format(**clean_target)

    @contextmanager
    def style_mode(self):
        self._styled = True
        try:
            yield self
        finally:
            self._styled = False

    def styled(self, target: dict | list) -> str:

        with self.style_mode():
            rich_string: str = self(target)

        return rich_string

    @classmethod
    def parse_style(
        cls, style_pattern: str, keys: list[str], styles: list[str]
    ) -> Self:
        """Use transformed style_pattern as base for regex parser setup"""

        pattern: str = re.sub(r"\[.*?\]", "", style_pattern)

        return cls(
            pattern=pattern,
            keys=keys,
            style_pattern=style_pattern,
            styles=styles,
        )
