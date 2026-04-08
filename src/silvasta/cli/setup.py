from functools import wraps
from pathlib import Path

import typer
from loguru import logger

import silvasta.config.paths as sst

from ..utils.log import setup_logging
from ..utils.print import printer


def logger_catch(func):
    """Typer decorater BELOW 'app.command()', catch errors and log them via Loguru.
    Ensures metadata is preserved and errors are handled globally."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        with logger.catch(
            reraise=False
        ):  # Ensures no crash with standard traceback
            # loguru still writes the full error to sinks
            return func(*args, **kwargs)

    return wrapper


def attach_callback(
    app: typer.Typer, config: Path | None = None
):  # LATER: config_path=?
    """Register  single dispatcher callback to the app"""

    @app.callback()
    def dispatcher(
        ctx: typer.Context,
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Show debug logs"
        ),
        quiet: bool = typer.Option(
            False, "--quiet", "-q", help="Terminal output"
        ),
    ):
        # INFO: use for debug
        # printer(dir(ctx.parent))
        # printer(vars(ctx))
        # printer(ctx.info_name)

        if ctx.parent is None:
            main_callback(ctx, verbose, quiet, config)
        else:
            sub_callback(ctx)


def main_callback(
    ctx: typer.Context, verbose: bool, quiet: bool, config: Path | None = None
):
    """Setup logging (data, etc...) for app executed as main app"""

    printer.title(f"Welcome to {ctx.info_name}!")

    printer.title("Setup Config and Logging", style="cyan")

    print(config or sst.get_setting_file_path())

    # Setup logging
    level: str | None = "DEBUG" if verbose else None
    setup_logging(log_level_override=level, quiet=quiet)

    # LATER: check if config here makes sense


def sub_callback(ctx: typer.Context):
    """Provide information for subapps that help users to navigate"""

    printer.title(
        f"Launching sub command: {ctx.info_name}!",
        style="cyan",
    )
