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
