from functools import wraps

import typer
from loguru import logger

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


def main_callback(ctx: typer.Context, verbose: bool, quiet: bool):
    """Setup logging (data, etc...) for app executed as main app"""

    printer.title(f"Start of: {ctx.info_name}!")  # TEST: check apps and subapps
    # print(dir(ctx))

    # TODO: extend with data setup of sachmet
    # - check if and how data should or will be attached,
    # if in callback, this here and below is useless

    # Setup logging
    level: str | None = "DEBUG" if verbose else None
    setup_logging(log_level_override=level, quiet=quiet)


def sub_callback(name: str):
    """Provide information for subapps that help users to navigate"""
    printer.title(f"Start of: {name}!")  # TEST: check apps and subapps


def attach_callback(app: typer.Typer):
    """Register  single dispatcher callback to the app"""

    # TASK: rethink strategy

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
        if ctx.parent is None:
            main_callback(ctx, verbose, quiet)
        else:
            sub_callback(f"{ctx.parent}")  # TEST: check apps and subapps
