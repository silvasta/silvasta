from functools import wraps

import typer
from loguru import logger

from sstcore.config.manager import ConfigSetupParam

from ..utils import Printer, printer
from ..utils.log import LogParam, LogSetupResult, setup_logging


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


def attach_callback(app: typer.Typer, param: ConfigSetupParam | None = None):
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
    param: ConfigSetupParam | None = None,
):
    """Setup logging (data, etc...) for app executed as main app"""

    Printer.project_name = param.project_name if param else ""
    Printer.project_version = param.project_version if param else ""

    printer.title(f"Welcome to {ctx.info_name}!")
    printer.title("Setup Config and Logging", style="cyan")

    log_param: LogParam | None = param.log if param else None
    level: str | None = "DEBUG" if verbose else None

    result: LogSetupResult = setup_logging(
        log_level_override=level, quiet=quiet, param=log_param
    )
    if param:
        printer.title(f"Config File: {param.config_file}", style="cyan")
    else:
        printer.warn("Config File: Not provided by 'ConfigSetupParam'")

    printer.title(f"Log File: {result.log_file}", style="cyan")

    if result.selected_param.print_log_param:
        printer(result.selected_param)  # REMOVE: print: print_log_param = True


def sub_callback(ctx: typer.Context):
    """Provide information for subapps that help users to navigate"""

    printer.title(
        f"Launching sub command: {ctx.info_name}!",
        style="cyan",
    )
