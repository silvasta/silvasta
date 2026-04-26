from functools import wraps

import typer
from loguru import logger

from ..config import ConfigManager
from ..utils import printer, setup_logging
from ..utils.log import LogParam


def logger_catch(func):
    """Typer decorator BELOW 'app.command()', catch errors and log them via Loguru.
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
    app: typer.Typer, param: dict[str, str | LogParam] | None = None
):
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
        if ctx.parent is None:
            main_callback(ctx, verbose, quiet, param)
        else:
            sub_callback(ctx)


def main_callback(
    ctx: typer.Context,
    verbose: bool,
    quiet: bool,
    param: dict[str, str | LogParam] | None = None,
):
    """Setup logging (data, etc...) for app executed as main app"""

    printer.title(f"Welcome to {ctx.info_name}!")

    printer.title("Setup Config and Logging", style="cyan")

    if param is None:
        logger.warning("setup backup config manager for param")
        config: ConfigManager = ConfigManager.default_setup()
        param: dict[str, str | LogParam] = config.compose_setup_param()

    level: str | None = "DEBUG" if verbose else None
    setup_logging(log_level_override=level, quiet=quiet, param=param)


def sub_callback(ctx: typer.Context):
    """Provide information for subapps that help users to navigate"""

    printer.title(
        f"Launching sub command: {ctx.info_name}!",
        style="cyan",
    )
