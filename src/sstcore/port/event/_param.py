"""
Define the Shape of the DTO Input and Parameter

X --- --- --- --- --- --- --- --- --- --- [ topic: FileScan ] --- X
| title: Frame with Title on top of the Content                   |
X --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- X
| content: ...                 (maybe double line for transition) |
|          ...                                                    |

- No Header for title = None
- Mirror main frame topic for frame.topic = "", empty for None

                              DependencyLevel.sstcore.port.event[2]
"""

__all__: list[str] = [
    "LogInput",
    "CliInfoInput",
    "CliInput",
    # cli extensions
    "PanelInput",
    "BoxInput",
    "HeaderPresetInput",
    "StatusInput",
    "MarkdownInput",
    "LineInput",
    "LinePresetInput",
    "TableInput",
    "TablePresetInput",
    # all
    "MergedDtoInputs",
]


# TODO: external imports _privat
import dataclasses as _dc
import typing as _typing
from collections.abc import Callable as _Callable
from enum import auto
from typing import TypedDict

from .._types import EventTypes as _ET  # noqa: N814
from ..color import Color, ColorArg
from ..color import ColorArg as _ColorArg
from ..solid import OptionRegister
from ..structures import FieldSet, ParamSpec


class _Boxes(OptionRegister):  # MOVE: but where?
    """
    Select the Box around the Visualization

    - configured in util.print._boxes
    - exposed in util.print
    """

    CORNER = auto()
    ROUND = auto()
    UP = auto()
    DOWN = auto()
    MINI = auto()
    MINI_UP = auto()
    MINI_DOWN = auto()
    OPEN = auto()


class FrameSpec(ParamSpec):
    topic: str | None = ""
    topic_color: Color = Color.WHITE
    box: _Boxes = _Boxes.CORNER


class HeaderSpec(ParamSpec):
    """
    Explain:

    X --- --- --- --- --- --- --- --- --- --- [ topic: FileScan ] --- X
    | title: Frame with Title on top of the Content                   |
    X --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- X
    | content: ...                 (maybe double line for transition) |
    |          ...                                                    |

    - No Header for title = None
    - Mirror main frame topic for frame.topic = "", empty for None
    """

    title: str | None = None
    frame: FrameSpec = _dc.field(default_factory=FrameSpec)


def sanitize_kwargs(fields: FieldSet, **kwargs) -> _ET.StrDict:
    _kwargs: _ET.StrDict = dict(kwargs)

    if "frame" in fields and "frame" not in _kwargs:
        _kwargs["frame"] = FrameSpec.absorb(_kwargs)

    if "header" in fields and "header" not in _kwargs:
        # AI_TASK:  something went wrong with the ParamSpec.absorb
        # - find a solution that fixes the sanitation

        default_box: _Boxes = (
            _kwargs["frame"].box if "frame" in _kwargs else _Boxes.CORNER
        )
        # FIX:
        header_frame: FrameSpec = FrameSpec.absorb(
            _kwargs, prefix="header_", box=default_box
        )
        # FIX:
        _kwargs["header"] = HeaderSpec.absorb(_kwargs, frame=header_frame)

    return _kwargs


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class FrameTopicInput(TypedDict, total=False):
    topic: str
    topic_color: ColorArg


class FrameInput(FrameTopicInput, total=False):
    """Define the Border of one Header or Main Content"""

    box: _Boxes


class LogInput(_typing.TypedDict, total=False):
    level: str
    metrics: _ET.Map
    extra: _ET.Map


class CliInfoInput(_typing.TypedDict, total=False):
    infos: _ET.Map


class CliInput(CliInfoInput, total=False):
    color: _ColorArg


class HeaderBaseInput(TypedDict, total=False):
    title: str


class HeaderFrameInput(TypedDict, total=False):
    header_topic: str
    header_topic_color: ColorArg
    header_box: _Boxes | None  # None = Same as Main Content


class HeaderInput(HeaderBaseInput, HeaderFrameInput, total=False):
    """Combine Header with Frame Args"""


class PanelInput(CliInput, HeaderInput, FrameInput, total=False):
    """Full manual Panel configuration"""


class BoxInput(CliInput, HeaderInput, FrameTopicInput, total=False):
    """Panel configuration when `box` style is fixed by a Box preset."""


class HeaderPresetInput(CliInput, HeaderFrameInput, FrameInput, total=False):
    """Panel configuration when `title` is passed positionally."""


class StatusInput(CliInfoInput, HeaderFrameInput, FrameInput, total=False):
    """Panel configuration when `title` and `color` are fixed by preset."""


class MarkdownInput(CliInput, FrameInput, total=False):
    maxlen: int


class LinePresetInput(CliInput, HeaderFrameInput, total=False):
    """Line options when `title`/`stat` are computed by a preset."""


class LineInput(CliInput, HeaderInput, total=False):
    stat: _Callable[[_ET.Vec], str]


class TablePresetInput(CliInput, HeaderInput, FrameInput, total=False):
    """Table styling options when grid/headers are built by a factory method."""


class TableInput(TablePresetInput, total=False):
    """Full manual Table configuration."""

    col_names: _ET.Content[str]
    row_names: _ET.Content[str]
    corner: str


class MergedDtoInputs(
    TableInput, MarkdownInput, LineInput, LogInput, total=False
):
    """Combined spec space so @castarg discovers all Annotated casters once."""
