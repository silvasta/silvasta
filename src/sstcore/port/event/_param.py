"""
Define the Arguments and Parameter for the DTO Pipeline

-
"""

__all__: list[str] = [
    "Boxes",
    "ParamData",
    "FrameData",
    "FrameSpec",
    "HeaderData",
    "HeaderBaseSpec",
    # cli extensions
    "HeaderFrameSpec",
    "HeaderSpec",
    "sanitize_specs",
]

import dataclasses as _dc
import enum as _e
import typing as _typing
from typing import Any as _Any

from ..color import Color as _Color
from ..color import ColorArg as _ColorArg
from ..solid import BoxOption as _BoxOption


@_typing.dataclass_transform(kw_only_default=True)
class ParamData:
    """Base for stacked configuration dataclasses (FrameData, HeaderData, etc.)."""

    def __init_subclass__(cls, kw_only: bool = True, **kwargs: _Any):
        super().__init_subclass__(**kwargs)
        _dc.dataclass(kw_only=kw_only, **kwargs)(cls)


class Boxes(_BoxOption):  # MOVE:  but where?
    CORNER = _e.auto()
    ROUND = _e.auto()
    UP = _e.auto()
    DOWN = _e.auto()
    MINI = _e.auto()
    MINI_UP = _e.auto()
    MINI_DOWN = _e.auto()
    OPEN = _e.auto()


class FrameData(ParamData):
    """The Box around the Renderable - supplies Content and Frame"""

    topic: str | None = ""
    topic_color: _Color = _Color.WHITE
    box: Boxes = Boxes.CORNER


class FrameSpec(_typing.TypedDict, total=False):
    """Define the Border of one Header or Main Content"""

    topic: str
    topic_color: _ColorArg
    box: Boxes


class HeaderData(ParamData):
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
    frame: FrameData = _dc.field(default_factory=FrameData)


class HeaderBaseSpec(_typing.TypedDict, total=False):
    title: str


class HeaderFrameSpec(_typing.TypedDict, total=False):
    """Test"""

    header_topic: str
    header_topic_color: _ColorArg
    header_box: Boxes | None  # None = Same as Main Content


class HeaderSpec(HeaderBaseSpec, HeaderFrameSpec, total=False):
    """Combine Header with Frame Args"""


def sanitize_specs(fields: set[str], **kwargs):
    spec: dict[str, _Any] = dict(kwargs)

    if "frame" in fields and "frame" not in spec:
        frame_keys: set[str] = {
            field.name for field in _dc.fields(class_or_instance=FrameData)
        }
        frame_kw: dict[str, _Any] = {
            k: spec.pop(k) for k in list(spec) if k in frame_keys
        }
        if frame_kw:
            spec["frame"] = FrameData(**frame_kw)

    if "header" in fields and "header" not in spec:
        header_frame_kw: dict[str, _Any] = {
            k.removeprefix("header_"): spec.pop(k)
            for k in list(spec)
            if k.startswith("header_")
        }
        title: str | None = spec.pop("title", None)

        if title is not None or header_frame_kw:
            main_frame: FrameData | None = spec.get("frame")

            if header_frame_kw.get("box") is None and main_frame:
                header_frame_kw["box"] = main_frame.box

            spec["header"] = HeaderData(
                title=title,
                frame=FrameData(**header_frame_kw)
                if header_frame_kw
                else FrameData(),
            )

    return spec
