# sstcore/cli/app.py
import sys
from collections.abc import Callable
from typing import Any

import typer
from loguru import logger

from ..config.manager import ConfigSetupParam
from ..utils import Printer, printer
from ..utils.log import LogParam, LogSetupResult, setup_logging
from ..utils.print import ColorBox


class SafeTyper(typer.Typer):
    """A managed Typer application that automates logging registration,

    contextual callbacks, and local error mapping registries.
    """

    def __init__(self, *args, param: ConfigSetupParam | None = None, **kwargs):
        kwargs.setdefault("no_args_is_help", True)
        super().__init__(*args, **kwargs)

        self._param: ConfigSetupParam | None = param

        self._error_handlers: dict[
            type[BaseException], Callable[[Any], None]
        ] = {}

        self._attach_internal_callback()

    def register_error(self, exception: type[BaseException]):
        """Decorator: Handle local domain Exception by custom function"""

        def decorator(handler: Callable[[Any], None]):
            self._error_handlers[exception] = handler
            return handler

        return decorator

    def __call__(self, *args, **kwargs):
        """Unified intercept run loop separating unexpected panics from planned exits."""
        try:
            # 1. Lock down unexpected critical exceptions via loguru tracking
            with logger.catch(reraise=True, exclude=(typer.Exit, typer.Abort)):
                return super().__call__(*args, **kwargs)

        except typer.Exit, typer.Abort:
            raise  # Let Typer handle its normal command loop exits cleanly

        except Exception as error:
            # 2. Intercept project-specific overrides outside loguru tracing
            if handler := self._error_handlers.get(type(error)):
                try:
                    handler(error)
                    raise typer.Exit(code=1)
                except Exception as handler_exc:
                    logger.critical(
                        f"Custom error handler crashed: {handler_exc}"
                    )

            # 3. Fallback tracking for completely unhandled structural issues
            logger.exception("CLI tracking execution failed critically")
            sys.exit(1)

    def _attach_internal_callback(self):
        """Implicitly binds the structural logging parameter dispatcher logic."""

        @self.callback()
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
                self._run_main_callback(ctx, verbose, quiet)
            else:
                self._run_sub_callback(ctx)

    def _run_main_callback(
        self, ctx: typer.Context, verbose: bool, quiet: bool
    ):
        """Execute full environment logging bootstrap pipelines on root execution"""

        log_level_override: str | None = "DEBUG" if verbose else None

        if self._param:
            Printer.project_name = self._param.project_name
            Printer.project_version = self._param.project_version

        printer.title(f"Welcome to {ctx.info_name}!")
        printer.header("Setup Config and Logging")

        log_param: LogParam = self._param.log if self._param else LogParam()

        result: LogSetupResult = setup_logging(
            log_level_override=log_level_override, quiet=quiet, param=log_param
        )

        c: ColorBox = printer.colorbox(mode="bold")
        _file = c.blue("Config File")
        _param = c.yellow("ConfigSetupParam")

        if self._param:
            if (path := self._param.config_file).is_file():
                printer.title(path, title="Config File")
            else:
                printer.danger(f"{_file} provided by {_param} not on disk!")
                printer(self._param)
                logger.error(f"Missing config file: {path=}")
        else:
            printer.warn(f"Typer Setup: {_file} not provided by {_param}")

        printer.title(text=result.log_file, title="Log File")

        if result.setup_source == "param" and self._param:
            result.setup_source = self._param.log_source

        if log_param.print_at_setup:
            printer(result)
        else:
            printer(
                f"  {printer.colors.yellow('LogParam')} Source: {result.setup_source}"
            )

    def _run_sub_callback(self, ctx: typer.Context):
        """Alerts the operator when descending into localized commands scopes."""
        printer.title(f"Launching sub command: {ctx.info_name}!")
