import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import typer
from loguru import logger

from ..config import get_config
from ..config.manager import ConfigSetupParam
from ..utils import Printer, printer
from ..utils.log import LogSetupResult, setup_logging
from . import canvas

# AI: is this a reasonable simplification or either confusing?
type ErrorHandlerDict = dict[type[BaseException], Callable[[Any], None]]


class SafeTyper(typer.Typer):
    """
    Lead custom Setup for Typer app with Log and Error handling

    - Provide Framework with basic callback attach and start prints
    - Ensure Loguru is ready and loaded with custom settings
    - Protect CLI display from Errors with registred Exception handlers

    """

    def __call__(self, *args, **kwargs):
        """Run Typer app as usual but intercept critical Errors"""

        try:  # Regular Typer Execution (No logger here!)
            return super().__call__(*args, **kwargs)

        except typer.Exit, typer.Abort:  # WARN: tuple?
            raise

        except Exception as error:
            if handler := self._error_handlers.get(type(error)):
                try:
                    handler(error)
                    sys.exit(1)  # Force OS exit, skip Typer teardown
                except Exception as handler_exc:
                    logger.critical(
                        f"Custom error handler crashed: {handler_exc}"
                    )
                    sys.exit(2)

            # This is the ONLY place an unhandled error gets logged!
            logger.exception("CLI tracking execution failed critically")
            sys.exit(1)

    def register_error(self, exception: type[BaseException]):
        """Decorator: Attach Exception with custom Handler to Registry"""

        def decorator(handler: Callable[[Any], None]):
            self._error_handlers[exception] = handler
            return handler

        return decorator

    #  TASK: config: improve param or setup/load config inside startup

    def __init__(
        self,
        *args,
        param: ConfigSetupParam | None = None,
        **kwargs,
    ):
        kwargs.setdefault("no_args_is_help", True)
        super().__init__(*args, **kwargs)

        logger.info(f"Start of Setup: {type(self).__name__}")

        # AI: check the get_config from sstcore and from sachmis,
        # - discuss if 1 clear setup together with log here could make sense,
        #   or other options how to synchronize the pipeline

        # AI: here is first usage of get_config() (compare with logs)
        self._param: ConfigSetupParam = param or get_config().setup_info
        self._inject_project_param_to_printer()

        self._error_handlers: ErrorHandlerDict = {}
        self._attach_internal_callback()

    def _inject_project_param_to_printer(self):
        # NOTE: maybe do this in config setup?
        # (is already done there, the params come from there...)
        project_name: str = self._param.project_name or "EmptySetupParam"
        project_version: str = self._param.project_version or "0.0.0"
        Printer.project_name = project_name
        Printer.project_version = project_version

    def _attach_internal_callback(self):
        """Dispatch callback depending on Main or Subapp"""

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
        """Setup Logging and confirm settings"""

        printer.title(f"Welcome to {ctx.info_name}!")
        printer.header("Setup Config and Logging")

        # TASK: maybe here: setup config?

        canvas.main_callback_config_setup(self._param)

        result: LogSetupResult = setup_logging(
            log_level_override="DEBUG" if verbose else None,
            quiet=quiet,
            param=self._param.log if self._param else None,
        )
        self.log_file: Path | None = result.log_file

        canvas.main_callback_log_setup(result)

    def _run_sub_callback(self, ctx: typer.Context):
        """Print Nice Title for launching Subapp"""
        printer.title(f"Launching attached App: {ctx.info_name}!")
