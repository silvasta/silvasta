"""
Compose CliMixins

- Atomize: 1 class with 1 method __cli__

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

from ....format.color import colorize
from ....format.convert import dict_to_list
from ....format.reflect import rich, text
from ....port.event.dto import (
    LineDTO,
    MarkdownDTO,
    PanelDTO,
    Renderable,
    TableDTO,
)
from ...print.toolbox import dict_table, path_exists_table
from ._basics import data


class MarkdownMixin:
    """Render class text as Markdown, falling back to public attributes."""

    def __cli__(self) -> MarkdownDTO:  # LATER: this as DTO Template
        content_field = "_markdown_text"
        content: str = (
            text(self, attrs=[content_field])
            or f"# {self}\n- Nothing defined in content field: '{content_field}'"
        )
        return MarkdownDTO(text=content)


class LineMixin:
    """Show classname as single colored line"""

    def __cli__(self) -> LineDTO:
        return LineDTO(text=str(self), style="cyan")


class TableMixin:
    """Create table from public attributes"""

    def __cli__(self) -> TableDTO:
        return TableDTO.from_row_dicts(data(self))


class PanelMixin:
    """Show specific class attributes defined in _panel_data"""

    @property
    def _panel_data(self) -> Renderable | list[Renderable]:
        """Provide subhook for override custom panel data"""
        # FIX: Renderable
        return dict_to_list(data(self), sep=": ")

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            text=self._panel_data,
            title=rich(self),
            frame="cyan",  # NEXT: color not hardcoded!!
        )


class SlimPanelMixin:
    """Show class name in panel with module path in title"""

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            text=colorize.modules(self),
            title=rich(self),
            frame="cyan",  # NEXT: color not hardcoded!!
        )


class FullPanelMixin:
    """Show debug dict table with full vars"""

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            # FIX: Renderable
            text=dict_table(target=vars(self), show_type=True),
            title=rich(self),
            frame="cyan",  # NEXT: color not hardcoded!!
        )


class PathPanelMixin:
    """Show _panel_paths with check if they exists"""

    @property
    def _panel_paths(self) -> list[Path]:
        return []

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            # FIX: Renderable
            text=path_exists_table(self._panel_paths),
            title=rich(self),
            frame="cyan",  # NEXT: color not hardcoded!!
        )
