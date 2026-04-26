from pathlib import Path
from typing import Annotated

import typer

# TASK: Find proper generalized annotations
# - check:
#   - sachmis
#   - grab
#   - file-analyzer
#   - tyrus
#   - SysCo


DryRun = Annotated[
    bool,
    typer.Option(
        "--dry",
        help="Simulate pipeline without execution",
    ),
]


Root = Annotated[
    # TEST: useful? no collision??
    Path | None,
    typer.Option(
        "--root",
        "-r",
        help="Select root for current task",
    ),
]

File = Annotated[
    # WARN: check collision with Files
    Path | None,
    typer.Option(
        "--file",
        "-f",
        help="Add file from path",
    ),
]
Files = Annotated[
    # WARN: check collision with File
    list[Path] | None,
    typer.Option(
        "--files",
        "-f",
        help="Add files from paths",
    ),
]
