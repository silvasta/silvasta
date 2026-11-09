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
    "FrameSpec",
    "HeaderSpec",
    "sanitize_kwargs",
    # base inputs
    "FrameTopicInput",
    "FrameInput",
    "HeaderBaseInput",
    "HeaderFrameInput",
    "HeaderInput",
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


import dataclasses as _dc
import typing as _t
from collections.abc import Callable, Mapping, MutableMapping
from enum import auto

from .._types import EventTypes as _ET  # noqa: N814
from ..color import Color, ColorArg
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
    Configure Header above Main Content

    - No Header for title = None
    - Mirror main frame topic for frame.topic = "", empty for None
    """

    title: str | None = None
    frame: FrameSpec = _dc.field(default_factory=FrameSpec)

    @classmethod
    def absorb(
        cls,
        kwargs: Mapping[str, _t.Any],
        /,
        *,
        prefix: str = "",
        destroy: bool = True,
        **defaults: _t.Any,
    ) -> _t.Self:
        """Absorb Header fields and nested `header_*` FrameSpec fields."""
        if "frame" not in defaults:
            main_frame = kwargs.get("frame")
            default_box: _Boxes = (
                main_frame.box
                if isinstance(main_frame, FrameSpec)
                else _Boxes.CORNER
            )
            box_key = f"{prefix}header_box"
            if box_key in kwargs and kwargs[box_key] is None:
                if destroy and isinstance(kwargs, MutableMapping):
                    kwargs.pop(box_key)
                else:
                    kwargs: _ET.StrDict = {
                        k: v for k, v in kwargs.items() if k != box_key
                    }

            defaults["frame"] = FrameSpec.absorb(
                kwargs,
                prefix=f"{prefix}header_",
                destroy=destroy,
                box=default_box,
            )
        return super().absorb(
            kwargs, prefix=prefix, destroy=destroy, **defaults
        )


_SPEC_FIELDS: Mapping[str, type[ParamSpec]] = {
    "frame": FrameSpec,
    "header": HeaderSpec,
}


def sanitize_kwargs(fields: FieldSet, **kwargs) -> _ET.StrDict:
    """Pack flat kwargs into nested ParamSpec expected by target DTO"""
    for name, spec_cls in _SPEC_FIELDS.items():
        if name in fields and name not in kwargs:
            kwargs[name] = spec_cls.absorb(kwargs)
    return kwargs


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class FrameTopicInput(_t.TypedDict, total=False):
    topic: str
    topic_color: ColorArg


class FrameInput(FrameTopicInput, total=False):
    """Define the Border of one Header or Main Content"""

    box: _Boxes


class LogInput(_t.TypedDict, total=False):
    level: str
    metrics: _ET.Map
    extra: _ET.Map


class CliInfoInput(_t.TypedDict, total=False):
    infos: _ET.Map


class CliInput(CliInfoInput, total=False):
    color: ColorArg


class HeaderBaseInput(_t.TypedDict, total=False):
    title: str


class HeaderFrameInput(_t.TypedDict, total=False):
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
    stat: Callable[[_ET.Vec], str]


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
