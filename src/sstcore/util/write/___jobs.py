"""
Prepare Infrastructure for Standardized Writer Access

                                                 DependencyLevel[0]
"""

# TASK: JobRegistry?

from ...port import annotate as _a
from ._typer import StubTyper

demo_typer = StubTyper()


def jobs(sig) -> tuple[_a.StubJob3, ...]:
    return (
        _a.StubJob3(
            kind=_a.JobKind.STACK,
            public="DTO_STACK",
            class_name="GreeterEmpty",
            package="sstcore.brick.stack",
            stub_file="_stubs/_random.pyi",
            payload={
                "schema": demo_typer.schema(),
                "call": sig,
                "prefix": "Greeter",
            },
        ),
    )
