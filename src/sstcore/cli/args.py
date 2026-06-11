from pathlib import Path
from typing import Annotated

import typer

# IMPORTANT: Save, store args to config (if possible)
# TASK: Find proper generalized annotations
# - check:
#   - sachmis
#   - grab
#   - file-analyzer
#   - tyrus
#   - SysCo

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###  Boot
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

SettingFile = Annotated[
    Path | None,
    typer.Option(
        "--json",
        "-j",
        help="Override path to json settings file",
    ),
]

Verbose = Annotated[
    bool,
    typer.Option(
        "--verbose",
        "-v",
        help="Force verbose DEBUG logs",
    ),
]
Quiet = Annotated[
    bool,
    typer.Option(
        "--quiet",
        "-q",
        help="Silence terminal outputs",
    ),
]

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###  Common
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
DryRun = Annotated[
    bool,
    typer.Option(
        "--dry",
        help="Simulate pipeline without execution",
    ),
]


Root = Annotated[
    Path | None,
    typer.Option(
        "--root",
        "-r",
        help="Select root for current task",
    ),
]

# IDEA: this ad function/factory for customization
File = Annotated[
    # WARN: check collision with Files
    Path | None,
    typer.Option(
        "--file",
        "-f",
        help="Add file from path",
        # IDEA: help="Select {file_name} file by path",
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

Write = Annotated[
    bool,
    typer.Option(
        "--write",
        "-w",
        help="Write the current status to disk",
    ),
]
