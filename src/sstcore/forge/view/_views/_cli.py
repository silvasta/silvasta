"""
Compose CliMixins

- Atomize: 1 class with 1 method __cli__

               DependencyLevel.sstcore.forge.view._views[c.2.4.0.0]
"""

from typing import Any

__all__: list[str] = [
    "LineMixin",
    "TableMixin",
    "SlimPanelMixin",
    "PanelMixin",
    "FullPanelMixin",
    "PathPanelMixin",
    "PathTabelMixin",
]

from collections.abc import Iterable
from dataclasses import fields, is_dataclass
from pathlib import Path

from ....brick import reflect
from ....brick.color import colorize
from ....brick.format import norm
from ....brick.reflect import scan
from ....port.color import Color
from ....port.event.dto import LineDTO, MarkdownDTO, PanelDTO, TableDTO
from ..factory import TableViewDTO
from ..factory import dto_factory as _factory


class MarkdownMixin:
    """Render class text as Markdown, falling back to public attributes."""

    def __cli__(self) -> MarkdownDTO:
        content_field = "_markdown_text"
        content: str = (
            reflect.text(self, attrs=[content_field])
            or f"# {self}\n- Nothing defined in content field: '{content_field}'"
        )
        return MarkdownDTO(content)


class LineMixin:
    """Show classname as single colored line"""

    def __cli__(self) -> LineDTO:
        return LineDTO((str(self),), color=Color.AZURE)


class TableMixin:
    """Create table from public attributes"""

    def __cli__(self) -> TableDTO:
        return TableViewDTO.from_rows(scan.data(self))


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


def _iter_attrs(unit, /) -> Iterable[Any]:
    """Scan Instance and provide dataclass fields or __dict__ vars"""
    if is_dataclass(unit):
        for field in fields(unit):
            yield getattr(unit, field.name)
    elif hasattr(unit, "__dict__"):
        yield from vars(unit).values()


class PathPanelMixin:
    """Show _panel_paths or find all Paths"""

    def _panel_paths(self) -> Iterable[Path]:
        for val in _iter_attrs(self):
            if isinstance(val, Path):
                yield val

    def _format_path(self, path: Path, /) -> str:
        return colorize.path(path)

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            tuple(self._format_path(p) for p in self._panel_paths()),
        )


def _iter_fields(unit, /) -> Iterable[tuple[str, Any]]:
    """Scan Instance and provide dataclass fields or __dict__ vars"""
    if is_dataclass(unit):
        for field in fields(unit):
            yield field.name, getattr(unit, field.name)
    elif hasattr(unit, "__dict__"):
        yield from vars(unit).items()


class PathTabelMixin:
    """Show _panel_paths with check if they exists"""

    def _panel_paths(self) -> Iterable[tuple[str, Path]]:
        for name, attr in _iter_fields(self):
            if isinstance(attr, Path):
                yield name, attr

    def _format_path(self, path: Path, /) -> str:
        return colorize.path(path)

    def __cli__(self) -> TableDTO:
        return _factory.table.rows(
            {
                name: ("✅" if path.exists() else "", self._format_path(path))
                for name, path in self._panel_paths()
            },
            # NEXT: figure out viz
            title=f"{self}",
            # title=reflect.rich(self),
            topic=f"{self}",
        )
