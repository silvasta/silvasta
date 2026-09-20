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

from ...port.event.dto import LineDTO, MarkdownDTO, PanelDTO, TableDTO
from ..color import colorize
from ..labor import reflect
from ..norm import transform


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
        return LineDTO(str(self), style="cyan")


class TableMixin:
    """Create table from public attributes"""

    def __cli__(self) -> TableDTO:
        return TableDTO.from_row_dicts(reflect.data(self))


class PanelMixin:
    """Show specific class attributes defined in _panel_data"""

    @property
    def _panel_data(self) -> str | list[str]:
        """Provide subhook for override custom panel data"""
        # FIX: Renderable
        return transform.dict_to_list(reflect.data(self), sep=": ")

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            self._panel_data,
            title=reflect.rich(self),
            frame="cyan",  # NEXT: color not hardcoded!!
        )


class SlimPanelMixin:
    """Show class name in panel with module path in title"""

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            colorize.modules(self),
            title=reflect.rich(self),
            frame="cyan",  # NEXT: color not hardcoded!!
        )


class FullPanelMixin:
    """Show debug dict table with full vars"""

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            # FIX: Renderable
            colorize.dict_table(target=vars(self), show_type=True),
            title=reflect.rich(self),
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
            colorize.path_exists_table(self._panel_paths),
            title=reflect.rich(self),
            frame="cyan",  # NEXT: color not hardcoded!!
        )
