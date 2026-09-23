"""
Prepare Infrastructure for Standardized Writer Access

                                                 DependencyLevel[0]
"""

# TASK: JobRegistry?

from dataclasses import dataclass

from ...brick.stack._example import ANSI_STACK, DTO_STACK, STRING_STACK
from ._typer import StackTyper

#  LINE: -- Tasks -- -- - -- -- - -- -- - -- -- - -- -- - -- --


TASKS = [
    {
        "typer": StackTyper(DTO_STACK, class_name="Greeter"),
        "target_module": "sstcore.brick.stack",
        "file_name": "_stubs/_random.pyi",
    },
    # Future typers go here
]


def sync_stubs():
    for task in TASKS:
        _content = task["typer"].draw()
        # target_dir = resolve_package_path(task["target_module"])
        # file_path = target_dir / task["file_name"]
        # Use your PathGuard here to handle the file write


#  LINE: -- Jobs -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True)
class StubJob:
    public: str  # binding in __init__.py  e.g. "DTO_STACK"
    prefix: str  # Greeter / Printer
    package: str | None = None  # override; else infer


JOBS = [
    StackTyper(DTO_STACK, StubJob("DTO_STACK", "Greeter")),
    StackTyper(ANSI_STACK, StubJob("ANSI_STACK", "Printer")),
    StackTyper(STRING_STACK, StubJob("STRING_STACK", "Text")),
    # later: StackTyper(COLOR_BOX, StubJob("box", "Color", package="sstcore.brick.color")),
]


# def ____main() -> None:
#     overlay_lines: dict[str, list[str]] = {}
#     for job in JOBS:
#         job.write(guard)
#         pkg = job.job.package or public_package_name(
#             module_name_of(job.source)
#         )
#         overlay_lines.setdefault(pkg, []).append(
#             f"from ._stubs._{job.job.prefix.lower()} import {job.job.prefix}Empty\n"
#             f"{job.job.public}: {job.job.prefix}Empty"
#         )
