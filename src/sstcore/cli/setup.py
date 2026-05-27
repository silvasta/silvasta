import random
from functools import wraps

import typer
from loguru import logger
from rich.panel import Panel

from ..config.manager import ConfigSetupParam
from ..utils import Printer, printer
from ..utils.log import LogParam, LogSetupResult, setup_logging

# TASK: setup config
# NEXT: general config setup, working over distributed projects!


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
    warn_no_file: bool = True,
):
    """Setup logging (data, etc...) for app executed as main app"""

    level: str | None = "DEBUG" if verbose else None

    Printer.project_name = param.project_name if param else ""
    Printer.project_version = param.project_version if param else ""

    # NEXT: set default style

    match random.randint(1, 4):
        # match 4:
        case 1:
            printer.title(f"Welcome to {ctx.info_name}!")
        case 2:
            printer.panel(
                f"[white]Welcome to {ctx.info_name}![/]", style="cyan"
            )
        case 3:
            printer.panel(
                f"[bold white]Welcome to {ctx.info_name}![/]",
                border_style="white on cyan",
                padding=(1, 1),
            )
        case 4:
            printer(
                Panel(
                    Panel(
                        f"[white]Welcome to {ctx.info_name}![/]",
                        style="cyan on black",
                    ),
                    style="cyan",
                ),
            )

    printer.title("Setup Config and Logging", style="cyan")

    log_param: LogParam = param.log if param else LogParam()

    result: LogSetupResult = setup_logging(
        log_level_override=level, quiet=quiet, param=log_param
    )

    if param:
        if (path := param.config_file).is_file():
            printer.panel(
                f"[white]{path}[/]",
                title="Config File",
                title_align="left",
                style="cyan",
            )
        else:
            printer.danger("Config file provided by param doesn't exists!")
            printer(param)
            logger.error(f"Missing config file: {path=}")
    else:
        if warn_no_file:
            printer.warn("Config File: Not provided by 'ConfigSetupParam'")

    printer.panel(
        f"[white]{result.log_file}[/]",
        title="Log File",
        title_align="left",
        style="cyan",
    )

    if result.setup_source == "param" and param:
        result.setup_source: str = param.log_source

    if log_param.print_at_setup:
        printer(result)
    else:
        printer(f"Log param source: {result.setup_source}")


def sub_callback(ctx: typer.Context):
    """Provide information for subapps that help users to navigate"""

    printer.title(
        f"Launching sub command: {ctx.info_name}!",
        style="cyan",
    )
