"""
Draft

-
"""


class PanelDTO[
    H: HeaderData[_Any] = HeaderData[FrameData],
    F: FrameData = FrameData,
](CliDTO[_Vec], name="panel"):
    """Store Data to Render in Box"""

    header: H = _param_field(HeaderData)
    frame: F = _param_field(FrameData)

    @classmethod
    def create1(
        cls,
        content: tuple[str, ...],
        *,
        header: HeaderData | None = None,
        frame: FrameData | None = None,
    ) -> _typing.Self:
        return cls(
            content=content,
            header=header or HeaderData(),
            frame=frame or FrameData(),
        )

    @classmethod
    def create2(
        cls, content: tuple[str, ...], **kw: Unpack[HeaderFrame]
    ) -> _typing.Self:
        frame_spec = FrameSpec(
            **{k: v for k, v in kw if k in FrameSpec().keys()}
        )
        header_spec = HeaderSpec(
            **{k: v for k, v in kw if k in HeaderSpec().keys()}
        )
        return cls(
            content=content,
            header=HeaderData(**header_spec),
            frame=FrameData(**frame_spec),
        )

    @classmethod
    def create3[T: PanelDTO](
        cls, content: tuple[str, ...], *, x: type[T], **kw: Unpack[HeaderFrame]
    ) -> T:
        frame_spec = FrameSpec(
            **{k: v for k, v in kw if k in FrameSpec().keys()}
        )
        header_spec = HeaderSpec(
            **{k: v for k, v in kw if k in HeaderSpec().keys()}
        )
        return cls(  # ty:ignore
            content=content,
            header=HeaderData(**header_spec),
            frame=FrameData(**frame_spec),
        )
