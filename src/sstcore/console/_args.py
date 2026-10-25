"""
Prepare Arguments and Options for Typer

- UNDER CONSTRUCTION!

- Provide ready-to-use Annotations
- Build custom Annotations with Factory


Example with module import:
    from sstcore.cli import sargs
    from project.cli import args

    @app.command()
    def typer_func(task: args.Task, dry_run: sargs.DryRun): ...

"""

__all__: list[str] = [
    # Option Factories
    "enum_opt",
    "file_opt",
    "files_opt",
    "flag_opt",
    "filter_opt",
    # Boot Annotations
    "SettingFile",
    "Verbose",
    "Quiet",
    # Frequently Used Annotations
    "CleanState",
    "DryRun",
    "Write",
    "Root",
    "OutputFile",
    "LogFile",
    "File",
    "Files",
    # Filter Annotations
    "Include",
    "Exclude",
    "RequireAll",
    "Hidden",
]


from enum import Enum
from pathlib import Path
from typing import Annotated, Any

import typer


def enum_opt[EnumT: Enum](
    enum_class: type[EnumT], help_text: str = "", *flags: str
) -> Any:
    """Inject {value: Name} mapping into the help string of an IntEnum."""
    mapping: str = ", ".join(f"{m.value}: {m.name}" for m in enum_class)
    full_help_text: str = f"{help_text} [{mapping}]".strip()
    return typer.Option(None, *flags, help=full_help_text)


def flag_opt(help_text: str, *flags: str, default: bool = False) -> Any:
    """Generates Typer metadata for boolean flags."""
    return typer.Option(default, *flags, help=help_text)


def filter_opt(help_text: str, *flags: str) -> Any:  # LATER: other than Filter?
    """Generates Typer metadata for filter lists supporting comma-separated strings."""
    return typer.Option(
        None,
        *flags,
        help=help_text,
        callback=_parse_keywords,
    )


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


#  LINE: -- Boot -- -- - -- -- - -- -- - -- -- - -- -- - -- --


SettingFile = Annotated[
    Path | None,
    file_opt("json settings", "--json", "-j"),
]

Verbose = Annotated[
    bool,
    flag_opt("Force verbose DEBUG logs", "--verbose", "-v"),
]

Quiet = Annotated[
    bool,
    flag_opt("Silence terminal outputs", "--quiet", "-q"),
]


#  LINE: -- Frequently Used -- -- - -- -- - -- -- - -- -- - -- -- - -- --


CleanState = Annotated[
    bool,
    flag_opt("Clean existing and start from fresh state", "--clean", "-c"),
]

DryRun = Annotated[
    bool, flag_opt("Simulate pipeline without execution", "--dry")
]

Write = Annotated[
    bool, flag_opt("Write the current status to disk", "--write", "-w")
]

Root = Annotated[
    Path | None,
    typer.Option(
        None,
        "--root",
        "-r",
        help="Select root for current task",
        dir_okay=True,
        # IDEA: flag_opt **kwargs??
        file_okay=False,
    ),
]

OutputFile = Annotated[
    Path | None,
    file_opt("Output", "--out", "-o"),
]

LogFile = Annotated[
    Path | None,
    file_opt("Log", "--log", "-l"),
]

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


#  LINE: -- Filter -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _parse_keywords(values: list[str] | None) -> list[str]:
    """
    Allows both: -i .py -i .rs  AND  -i .py,.rs

    Returns a list to match type annotations while maintaining order and dropping duplicates
    """
    if not values:
        return []
    return list(
        dict.fromkeys(
            item.strip()
            for v in values
            for item in v.split(",")
            if item.strip()
        )
    )


Include = Annotated[
    list[str] | None,
    filter_opt("Add to require_any ", "--include", "-i"),
]

Exclude = Annotated[
    list[str] | None,
    filter_opt("Add to exclude ", "--exclude", "-e"),
]

RequireAll = Annotated[
    list[str] | None,
    filter_opt("Require all tokens", "--all", "-a"),
]

Hidden = Annotated[
    bool,
    flag_opt("Allow hidden files/dotfiles", "--hidden"),
]
