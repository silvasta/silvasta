from functools import wraps

import typer
from loguru import logger

from ..config.manager import ConfigSetupParam
from ..utils import Printer, printer
from ..utils.log import LogParam, LogSetupResult, setup_logging


def logger_catch(func):
    """Typer decorator BELOW 'app.command()', catch errors and log them via Loguru.
    Ensures metadata is preserved and errors are handled globally."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Exclude typer.Exit and typer.Abort so they bypass Loguru
        # and allow the CLI to shut down cleanly without a traceback.
        with logger.catch(
            reraise=False,
            exclude=(typer.Exit, typer.Abort),
        ):
            return func(*args, **kwargs)

    # IMPORTANT:
    printer.warn("logger_catch outdated! Check cli.engine.SafeTyper")

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
        # IMPORTANT:
        printer.warn("attach_callback outdated! Check cli.engine.SafeTyper")

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

    printer.title(f"Welcome to {ctx.info_name}!")

    printer.title("Setup Config and Logging")

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

    if log_param.print_at_setup:
        printer(result)
    else:
        printer(f"Log param source: {result.setup_source}")


def sub_callback(ctx: typer.Context):
    """Provide information for subapps that help users to navigate"""

    printer.title(f"Launching sub command: {ctx.info_name}!")
