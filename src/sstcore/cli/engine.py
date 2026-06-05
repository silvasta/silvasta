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
    """A managed Typer application that automates logging registration,

    contextual callbacks, and local error mapping registries.
    """

    def __init__(self, *args, param: ConfigSetupParam | None = None, **kwargs):
        kwargs.setdefault("no_args_is_help", True)
        super().__init__(*args, **kwargs)

        self._attach_config_setup_param(param)
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
                    # FIX: something  not nice...
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

    def _attach_config_setup_param(self, param: ConfigSetupParam | None):
        logger.info(f"Start of Setup: {self.__class__.__name__}")
        logger.remove()  # TASK: find or confirm best location
        param: ConfigSetupParam = param or get_config().setup_info
        Printer.project_name = param.project_name or "EmptySetupParam"
        Printer.project_version = param.project_version or "0.0.0"
        self._param: ConfigSetupParam | None = param

    def _run_main_callback(
        self, ctx: typer.Context, verbose: bool, quiet: bool
    ):
        """Execute full environment logging bootstrap pipelines on root execution"""

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
        """Alerts the operator when descending into localized commands scopes."""
        printer.title(f"Launching sub command: {ctx.info_name}!")
