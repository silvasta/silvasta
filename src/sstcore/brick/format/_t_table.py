from collections.abc import Callable
from string.templatelib import Interpolation
from typing import Any

from rich.console import RenderableType
from rich.text import Text

type Piece = RenderableType
type ViewFn = Callable[[Any, Interpolation], Piece]


class ViewTable:
    """Runtime type → view. Subclasses win via MRO walk."""

    def __init__(self) -> None:
        self._exact: dict[type, ViewFn] = {}

    def mount(self, target_type: type, view: ViewFn) -> None:
        self._exact[target_type] = view

    def resolve(self, obj_type: type) -> ViewFn | None:
        for cls in obj_type.__mro__:
            if cls in self._exact:
                return self._exact[cls]
        return None


DEFAULT_VIEWS = ViewTable()


def _style_text(text: str, spec: str, fallback: str) -> Text:
    return Text(text, style=spec or fallback)


def mount_builtin_views(table: ViewTable) -> None:
    table.mount(
        str,
        lambda v, i: _style_text(
            v,
            i.format_spec,
            "bold yellow",
        ),
    )
    table.mount(
        int,
        lambda v, i: (
            _style_text(
                format(v, i.format_spec or ""),
                i.format_spec and "" or "bold magenta",
                "bold magenta",
            )
            if False
            else _style_text(
                str(v),
                "" if looks_like_format_spec(i.format_spec) else i.format_spec,
                "bold magenta",
            )
        ),
    )
    table.mount(bool, lambda v, i: Text(str(v), style="green" if v else "red"))
    table.mount(type(None), lambda v, i: Text("None", style="dim italic"))
