"""
Compose CliMixins

- Atomize: 1 class with 1 method __cli__

                             DependencyLevel.sstcore.brick.views[0]
"""

__all__: list[str] = [
    "LineMixin",
    "TableMixin",
    "SlimPanelMixin",
    "PanelMixin",
    "FullPanelMixin",
    "PathPanelMixin",
]

from pathlib import Path

from ....brick import reflect
from ....brick.color import colorize
from ....brick.format import norm
from ....brick.reflect import scan
from ....port.event.dto import LineDTO, MarkdownDTO, PanelDTO, TableDTO


class MarkdownMixin:
    """Render class text as Markdown, falling back to public attributes."""

    def __cli__(self) -> MarkdownDTO:  # LATER: this as DTO Template
        content_field = "_markdown_text"
        content: str = (
            reflect.text(self, attrs=[content_field])
            or f"# {self}\n- Nothing defined in content field: '{content_field}'"
        )
        return MarkdownDTO(content)


class LineMixin:
    """Show classname as single colored line"""

    def __cli__(self) -> LineDTO:
        return LineDTO(str(self), style="cyan")  # ty:ignore


class TableMixin:
    """Create table from public attributes"""

    def __cli__(self) -> TableDTO:
        return TableDTO.from_row_dicts(scan.data(self))  # ty:ignore


class PanelMixin:
    """Show specific class attributes defined in _panel_data"""

    @property
    def _panel_data(self):
        # def _panel_data(self) -> str | list[str]:
        # TASK: new concept for that
        """Provide subhook for override custom panel data"""
        return norm.dict_to_list(scan.data(self), sep=": ")

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            self._panel_data,
            # TODO:
        )


class SlimPanelMixin:
    """Show class name in panel with module path in title"""

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            tuple(colorize.modules(self)),
            # TODO:
        )


class FullPanelMixin:
    """Show debug dict table with full vars"""

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            tuple("OutOfOrder..."),
            # tuple(colorize.dict_table(target=vars(self), show_type=True)),
            # title=invoke.rich(self),
            # TODO:
        )


class PathPanelMixin:
    """Show _panel_paths with check if they exists"""

    @property
    def _panel_paths(self) -> list[Path]:
        return []

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            tuple(colorize.path(p) for p in self._panel_paths),
            # title=invoke.rich(self),
            # frame="cyan",  # NEXT: color not hardcoded!!
        )
