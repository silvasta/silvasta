"""
Define the Public Interface of the CliDtoFactory

-
"""

__all__: list[str] = ["CliDtoFactory"]

from collections.abc import Sequence
from typing import Any, NoReturn

from ...port.event.dto import (
    GroupDTO,
    LineDTO,
    LogDTO,
    MarkdownDTO,
    PanelDTO,
    RuleDTO,
    TableDTO,
)
from ...port.view import Renderable

class CliDtoFactory:
    def __init__(self) -> NoReturn: ...
    @classmethod
    def __str__(cls) -> str: ...
    @classmethod
    def __repr__(cls) -> str: ...
    @classmethod
    def __rich__(cls) -> str: ...
    @classmethod
    def __cli__(cls) -> PanelDTO: ...
    @classmethod
    def __log__(cls) -> LogDTO: ...
    @classmethod
    def toolkit(cls, sort: bool = True) -> list[str]: ...

    # -----------------------------------------------------------------------
    # Basic Factory Methods
    # -----------------------------------------------------------------------

    @staticmethod
    def panel(
        content: Renderable | list[Renderable],
        *,
        title: str | None = None,
        expand: bool = True,
        **kwargs: Any,
    ) -> PanelDTO: ...
    @staticmethod
    def group(*items: Renderable) -> GroupDTO: ...
    @staticmethod
    def line(character: str = "─", *, style: str = "cyan") -> LineDTO: ...
    @staticmethod
    def rule(title: str = "", *, style: str = "cyan") -> RuleDTO: ...
    @staticmethod
    def markdown(
        text: str, *, header: int = 0, style: str = "white"
    ) -> MarkdownDTO: ...

    # -----------------------------------------------------------------------
    # Table Transformers
    # -----------------------------------------------------------------------

    @staticmethod
    def table_from_rows(
        rows: dict[str, Any | Sequence[Any]],
        *,
        corner: str = "",
    ) -> TableDTO: ...
    @staticmethod
    def table_from_cols(
        cols: dict[str, Sequence[Any]],
        *,
        corner: str = "",
    ) -> TableDTO: ...
    @staticmethod
    def table_from_records(
        records: Sequence[dict[str, Any]],
        headers: list[str] | None = None,
    ) -> TableDTO: ...
