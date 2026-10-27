"""
Define the Arguments and Parameter for the DTO Pipeline

                              DependencyLevel.sstcore.port.event[0]
"""

__all__: list[str] = [
    "_Boxes",
    # data
    "ParamSpec",
    "FrameSpec",
    "HeaderSpec",
    # kwargs
    "FrameInput",
    "HeaderBaseInput",
    "HeaderFrameInput",
    "HeaderInput",
    #
    "sanitize_specs",
]

import dataclasses as _dc
import typing as _typing
from enum import auto
from typing import Any as _Any

from ..color import Color, ColorArg
from ..solid import OptionRegister


@_typing.dataclass_transform(kw_only_default=True)
class ParamSpec:  # TODO: compare with Functor::ParamSpec
    """Base for dataclasses that parse Param Input (FrameSpec, HeaderSpec,..)"""

    def __init_subclass__(cls, kw_only: bool = True, **kwargs: _Any):
        super().__init_subclass__(**kwargs)
        _dc.dataclass(kw_only=kw_only, **kwargs)(cls)


class _Boxes(OptionRegister):
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
    """The Box around the Renderable - supplies Content and Frame"""

    topic: str | None = ""
    topic_color: Color = Color.WHITE
    box: _Boxes = _Boxes.CORNER


class FrameTopicInput(_typing.TypedDict, total=False):
    topic: str
    topic_color: ColorArg


class FrameInput(FrameTopicInput, total=False):
    """Define the Border of one Header or Main Content"""

    box: _Boxes


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


class HeaderBaseInput(_typing.TypedDict, total=False):
    title: str


class HeaderFrameInput(_typing.TypedDict, total=False):
    header_topic: str
    header_topic_color: ColorArg
    header_box: _Boxes | None  # None = Same as Main Content


class HeaderInput(HeaderBaseInput, HeaderFrameInput, total=False):
    """Combine Header with Frame Args"""


def sanitize_specs(fields: set[str], **kwargs: _Any) -> dict[str, _Any]:
    # MOVE: somehow into brick or forge, but how?
    # TODO: compare with Functor::ParamSpec
    spec: dict[str, _Any] = dict(kwargs)

    if "frame" in fields and "frame" not in spec:
        frame_keys: set[str] = {
            field.name for field in _dc.fields(class_or_instance=FrameSpec)
        }
        frame_kw: dict[str, _Any] = {
            k: spec.pop(k) for k in list(spec) if k in frame_keys
        }
        if frame_kw:
            spec["frame"] = FrameSpec(**frame_kw)

    if "header" in fields and "header" not in spec:
        header_frame_kw: dict[str, _Any] = {
            k.removeprefix("header_"): spec.pop(k)
            for k in list(spec)
            if k.startswith("header_")
        }
        title: str | None = spec.pop("title", None)

        if title is not None or header_frame_kw:
            main_frame: FrameSpec | None = spec.get("frame")

            if header_frame_kw.get("box") is None and main_frame:
                header_frame_kw["box"] = main_frame.box

            spec["header"] = HeaderSpec(
                title=title,
                frame=FrameSpec(**header_frame_kw)
                if header_frame_kw
                else FrameSpec(
                    box=main_frame.box if main_frame else _Boxes.CORNER
                ),
            )

    return spec
