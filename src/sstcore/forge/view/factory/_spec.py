"""
Define the Kwarg-Space for the Factory

-
"""

import dataclasses as _dc
from collections.abc import Iterable
from typing import Any, Literal, Self, TypedDict

from ....port.color import Color
from ....port.event.dto import FrameData
from ....port.event.dto import _Map as Map
from ....util.print import boxes

type Align = Literal["left", "center", "right"]


#  LINE: -- Strategy 1 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class CliCoreSpec(TypedDict, total=False):
    color: Color
    data: Map


class HeaderSpec[FSpec = FrameSpec](TypedDict, total=False):
    title: str | None
    header_topic: str | None  # Fast flat shortcut for the 90% case!
    header_frame: FSpec | FrameData


class FrameSpec(TypedDict, total=False):
    topic: str | None
    box: boxes.AllNames
    frame_color: Color | None


#  LINE: -- Strategy 2 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@classmethod
def from_spec(cls, spec: Map, *, prefix: str = "") -> Self:
    """Extract matching fields from a flat kwargs dict (with optional prefix)."""
    valid_fields = {f.name for f in _dc.fields(cls)}
    extracted: dict[str, Any] = {}
    for k, v in spec.items():
        if prefix and k.startswith(prefix):
            stripped = k.removeprefix(prefix)
            if stripped in valid_fields:
                extracted[stripped] = v
        elif not prefix and k in valid_fields:
            extracted[k] = v
    return cls(**extracted)


#  LINE: -- Strategy 3 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LineDtoSpec(CliCoreSpec, HeaderSpec, total=False):
    """Used by factory.line(content, **spec)"""


class MarkdownDtoSpec(CliCoreSpec, FrameSpec, total=False):
    """Used by factory.markdown(content, **spec)"""


class PanelDtoSpec(CliCoreSpec, HeaderSpec, FrameSpec, total=False):
    """Used by factory.panel(content, **spec)"""


class TableDtoSpec(CliCoreSpec, HeaderSpec, FrameSpec, total=False):
    """Used by factory.table(grid, **spec)"""

    col_names: Iterable[str]
    row_names: Iterable[str]
    corner: str


#  LINE: -- Strategy 4 -- -- - -- -- - -- -- - -- -- - -- -- - -- --
