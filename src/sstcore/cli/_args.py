"""
Prepare Argumens and Options for Typer

- UNDER CONSTRUCTION!

- Provide ready-to-use Annotations
- Build custom Annotations with Factory


Example with module import:
    from sstcore.cli import sargs
    from project.cli import args

    @app.command()
    def typer_func(task: args.Task, dry_run: sargs.DryRun): ...

"""

from enum import Enum
from pathlib import Path
from typing import Annotated, Any

import typer

# TODO: Find proper generalized annotations
# - check:
#   - sachmis
#   - grab
#   - file-analyzer
#   - tyrus
#   - sysco

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###  Factories
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def enum_opt[EnumT: Enum](
    enum_class: type[EnumT], help_text: str = "", *flags: str
) -> Any:
    """Inject {value: Name} mapping into the help string of an IntEnum."""
    mapping: str = ", ".join(f"{m.value}: {m.name}" for m in enum_class)
    full_help_text: str = f"{help_text} [{mapping}]".strip()
    return typer.Option(None, *flags, help=full_help_text)


def file_opt(
    desc: str, *flags: str, exists: bool = False, dir_okay: bool = True
) -> Any:
    """Generates Typer metadata for a single file option."""
    cli_flags: tuple[str, ...] = flags if flags else ("--file", "-f")
    return typer.Option(
        None,
        *cli_flags,
        help=f"Select {desc} file by path",
        exists=exists,
        dir_okay=dir_okay,
    )


def files_opt(desc: str, *flags: str, exists: bool = False) -> Any:
    """Generates Typer metadata for a multiple files option."""
    cli_flags = flags if flags else ("--files", "-F")
    return typer.Option(
        None,
        *cli_flags,
        help=f"Add {desc} files from paths",
        exists=exists,
    )


def flag_opt(help_text: str, *flags: str, default: bool = False) -> Any:
    """Generates Typer metadata for boolean flags."""
    return typer.Option(default, *flags, help=help_text)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###  Boot
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

# TEST:
SettingFile = Annotated[Path | None, file_opt("json settings", "--json", "-j")]
# SettingFile = Annotated[ # REMOVE: after test
#     Path | None,
#     typer.Option(
#         "--json",
#         "-j",
#         help="Override path to json settings file",
#     ),
# ]

# TEST:
Verbose = Annotated[
    bool,
    flag_opt("Force verbose DEBUG logs", "--verbose", "-v"),
]
# Verbose = Annotated[ # REMOVE: after test
#     bool,
#     typer.Option(
#         "--verbose",
#         "-v",
#         help="Force verbose DEBUG logs",
#     ),
# ]

# TEST:
Quiet = Annotated[
    bool,
    flag_opt("Silence terminal outputs", "--quiet", "-q"),
]
# Quiet = Annotated[ # REMOVE: after test
#     bool,
#     typer.Option(
#         "--quiet",
#         "-q",
#         help="Silence terminal outputs",
#     ),
# ]
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###  Common
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
# TEST:
CleanState = Annotated[
    bool,
    flag_opt("Clean existing and start from fresh state", "--clean", "-c"),
]
# CleanState = Annotated[
#     bool,
#     typer.Option(
#         "--clean",
#         "-c",
#         help="Clean existing and start from fresh state ",
#     ),
# ]
# TEST:
DryRun = Annotated[
    bool, flag_opt("Simulate pipeline without execution", "--dry")
]
# DryRun = Annotated[
#     bool,
#     typer.Option(
#         "--dry",
#         help="Simulate pipeline without execution",
#     ),
# ]
# TEST:
Write = Annotated[
    bool, flag_opt("Write the current status to disk", "--write", "-w")
]
# Write = Annotated[
#     bool,
#     typer.Option(
#         "--write",
#         "-w",
#         help="Write the current status to disk",
#     ),
# ]


# TEST:
Root = Annotated[
    Path | None,
    typer.Option(
        None,
        "--root",
        "-r",
        help="Select root for current task",
        dir_okay=True,
        file_okay=False,
    ),
]
# Root = Annotated[
#     Path | None,
#     typer.Option(
#         "--root",
#         "-r",
#         help="Select root for current task",
#     ),
# ]

# TEST:
OutputFile = Annotated[
    Path | None,
    file_opt("Output", "--out", "-o"),
]
# OutputFile = Annotated[
#     Path | None,
#     typer.Option(
#         "--out",
#         "-o",
#         help="Select OutputFile",
#     ),
# ]

# TEST:
LogFile = Annotated[
    Path | None,
    file_opt("Log", "--log", "-l"),
]
# LogFile = Annotated[
#     Path | None,
#     typer.Option(
#         "--log",
#         "-l",
#         help="Select Log File",
#     ),
# ]
# File = Annotated[
#     Path | None,
#     typer.Option(
#         "--file",
#         "-f",
#         help="Add file from path",
#     ),
# ]
# TEST:
File = Annotated[
    Path | None,
    file_opt("target"),
]
# TEST:
Files = Annotated[
    list[Path] | None,
    files_opt("target"),
]
# Files = Annotated[
#     list[Path] | None,
#     typer.Option(
#         "--files",
#         "-f",
#         help="Add files from paths",
#     ),
# ]
