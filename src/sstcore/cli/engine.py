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
from . import layout


class SafeTyper(typer.Typer):
    """
    Lead custom Setup for Typer app with Log and Error handling

    - Provide Framework with basic callback attach and start prints
    - Ensure Loguru is ready and loaded with custom settings
    - Protect CLI display from Errors with registred Exception handlers
    """

    #  TASK: config: improve param or setup/load config inside startup

    def __call__(self, *args, **kwargs):
        """Run Typer app as usual but intercept critical Errors"""

        # NEXT: check loguru setup in pipeline, excludes?
        # - where, who and when to intercept what, so far confusing...
        # - sometimes like doubled stack trace
        # Need:
        # - clear boundry which error is raised where!

        try:  # Lock down unexpected critical exceptions via loguru tracking
            exclude: tuple = (  # TEST:
                typer.Exit,
                typer.Abort,
                *self._error_handlers.keys(),
            )
            with logger.catch(reraise=True, exclude=exclude):
                return super().__call__(*args, **kwargs)

        except typer.Exit, typer.Abort:
            raise  # Let Typer handle its normal command loop exits cleanly

        except Exception as error:
            # 2. Intercept project-specific overrides outside loguru tracing
            if handler := self._error_handlers.get(type(error)):
                try:
                    handler(error)
                    sys.exit(1)  # NEXT: works, was before typer.Exit, why?

                except Exception as handler_exc:
                    logger.critical(
                        f"Custom error handler crashed: {handler_exc}"
                    )

            # 3. Fallback tracking for completely unhandled structural issues
            logger.exception("CLI tracking execution failed critically")
            sys.exit(1)

    def register_error(self, exception: type[BaseException]):
        """Decorator: Attach Exception with custom Handler to Registry"""

        def decorator(handler: Callable[[Any], None]):
            self._error_handlers[exception] = handler
            return handler

        return decorator

    def __init__(self, *args, param: ConfigSetupParam | None = None, **kwargs):
        kwargs.setdefault("no_args_is_help", True)
        super().__init__(*args, **kwargs)

        logger.info(f"Start of Setup: {self.__class__.__name__}")
        # Silence to avoide noisy logs and prints from bootstrap
        logger.remove()  # TASK: find or confirm best location

        self._param: ConfigSetupParam = param or get_config().setup_info
        self._inject_project_param_to_printer()

        self._error_handlers: dict[
            type[BaseException], Callable[[Any], None]
        ] = {}  # TODO: improve, new type?

        self._attach_internal_callback()

    def _inject_project_param_to_printer(self):
        project_name: str = self._param.project_name or "EmptySetupParam"
        project_version: str = self._param.project_version or "0.0.0"
        # TODO: check how it works with derivatives of Printer
        Printer.project_name = project_name
        Printer.project_version = project_version

    def _attach_internal_callback(self):
        """Dispatch callback depending on App is Main or Subapp"""

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

        # TASK: maybe here: setup config?

        printer.title(f"Welcome to {ctx.info_name}!")
        printer.header("Setup Config and Logging")

        layout.main_callback_config_setup(self._param)

        result: LogSetupResult = setup_logging(
            log_level_override="DEBUG" if verbose else None,
            quiet=quiet,
            param=self._param.log if self._param else None,
        )
        self.log_file: Path | None = result.log_file

        layout.main_callback_log_setup(result)

    def _run_sub_callback(self, ctx: typer.Context):
        """Print Nice Title for launching Subapp"""
        printer.title(f"Launching sub command: {ctx.info_name}!")
