"""
StubFile Typer that Generates and Writes '.pyi' Files

-
"""

__all__: list[str] = [
    "stub_typer",
]


from pathlib import Path

from ...brick.color import colorize
from ...util.path.guard import PathGuard
from ...util.print import printer


def stub_typer(path: Path):
    """Show tail log display"""

    move_old: Path = PathGuard.unique(path, ensure_parent=True)
    # NOTE: probably not needed, but still, some backup strategy!
    printer.title(f"{colorize.path(move_old)} ...", "StubFile")
