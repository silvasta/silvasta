import typing as _typing
from pathlib import Path

from ....port.color import Color as _Color
from ....port.event.dto import FrameData, HeaderData, PanelDTO


def main():
    content: tuple[str, ...] = (
        Path.cwd().name,
        Path.cwd().name,
        Path.cwd().name,
    )
    test: PanelDTO[HeaderData, FrameData] = PanelDTO(
        content,
        header=HeaderData(
            title="My First Header",
            frame=FrameData(topic="FolderScanner"),
        ),
        frame=FrameData(topic="Result Path List"),
    )

    _typing.reveal_type(test.header.frame)
    _typing.reveal_type(test.frame.topic)

    print("--- " * 5)
    print(test)
    print(repr(test))
    print("--- " * 5)
    print()

    class NextFrameData(FrameData):
        topic_color: _Color = _Color.WHITE
        frame_color: _Color | None = None

    next_header: HeaderData[NextFrameData] = HeaderData(
        frame=NextFrameData(topic="Sub")
    )

    next_test: PanelDTO[HeaderData[NextFrameData], NextFrameData] = PanelDTO(
        content,
        header=next_header,
        frame=NextFrameData(topic="Result Path List"),
    )

    _typing.reveal_type(next_test.frame)
    _typing.reveal_type(next_test.frame.topic_color)

    print("--- " * 5)
    print(next_test)
    print(repr(next_test))
    print("--- " * 5)
    print()


if __name__ == "__main__":
    main()
