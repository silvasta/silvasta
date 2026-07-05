import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import typer
from loguru import logger

from ..config import ConfigManager
from ..config.loader import ConfigLoader, default_config_loader
from ..utils.log import LogSetupResult, setup_logging
from ..utils.log.setup import setup_minimal_logging
from . import args, canvas

type ErrorHandlerDict = dict[type[BaseException], Callable[[Any], None]]


class SafeTyper(typer.Typer):
    """
    Lead Custom Typer App Setup with Config, Log and Error handling

    - Provide Framework with basic callback attach and start prints
    - Ensure Loguru is ready and loaded with custom settings
    - Protect CLI display from Errors with registered Exception handlers

    """

    @property
    def n_handler(self) -> int:
        return len(self._error_handlers)

    @property
    def exceptions_of_all_handler(self) -> list[type[BaseException]]:
        """List Exception class of all registred handler"""
        return list(self._error_handlers.keys())

    def __init__(self, config_loader: ConfigLoader | None = None, **kwargs):
        """Load Typer and prepare custom setup"""

        kwargs.setdefault("no_args_is_help", True)
        super().__init__(**kwargs)

        self._config_loader: ConfigLoader = (
            config_loader or default_config_loader
        )
        self._error_handlers: ErrorHandlerDict = {}
        self._attach_internal_callback()

    def __str__(self):
        return type(self).__name__

    # TODO: def __repr__(self): def __rich__(self):

    def register_error_handler(self, exception: type[BaseException]):
        """Decorator: Attach Exception with custom Handler to Registry"""

        # TODO: improve type, why attach Exception basically twice?
        # @app.register_error_handler(TuiSelectorError)
        # def handle_tui_selector(error: TuiSelectorError):
        #     printer.danger(f"Selector failed: {error}")
        # - use that handler always has first (or even single) argumentslike:
        # - error:Exception, grab this

        def decorator(handler: Callable[[Any], None]):
            self._error_handlers[exception] = handler
            return handler

        return decorator

    def __call__(self, *args, **kwargs):
        """Run Typer app as usual but intercept critical Errors"""
        try:
            return super().__call__(*args, **kwargs)

        except Exception as error:
            if handler := self._error_handlers.get(type(error)):
                try:
                    handler(error)
                    sys.exit(1)

                except SystemExit:
                    raise  #  Let handlers dictate their own exit codes

                except Exception as handler_fail:
                    logger.critical(f"Error handler failed: {handler_fail}")
                    logger.error(f"Initial Error: {error}")
                    sys.exit(2)

            # INFO: Fallback for unhandled structural issues
            logger.exception("CLI Execution: Critical Failure...")
            sys.exit(1)

    def _attach_internal_callback(self):
        """Dispatch callback for Main or Subapp"""

        @self.callback()
        def dispatcher(
            ctx: typer.Context,
            verbose: args.Verbose = False,
            quiet: args.Quiet = False,
            setting_file: args.SettingFile = None,
        ):
            if ctx.parent is None:
                self._run_main_callback(ctx, verbose, quiet, setting_file)
            else:
                self._run_sub_callback(ctx)

    def _run_main_callback(
        self,
        ctx: typer.Context,
        verbose: bool,
        quiet: bool,
        setting_file: Path | None,
    ):
        """Setup Config and Logging and show Status"""

        # Use minimal output for bootstap fails but shadow bootstap noise
        setup_minimal_logging("DEBUG" if verbose else "WARNING")

        config: ConfigManager = self._config_loader(setting_file)
        # Wait for Printer until Injection in config_loader is done!

        log_result: LogSetupResult = setup_logging(
            log_level_override="DEBUG" if verbose else None,
            quiet=quiet,
            param=config.settings.log,
        )
        if not quiet:
            canvas.safe_typer.intro(project_name=ctx.info_name)
            canvas.safe_typer.setup(config, self._config_loader, log_result)

    def _run_sub_callback(self, ctx: typer.Context):
        """Print Nice subapp title"""
        canvas.safe_typer.sub_callback(ctx.info_name or "subapp")

    def print_setup_status(self, show_all_exceptions=False):
        """Launch Summary of Status after assembly"""
        exceptions: list = self.exceptions_of_all_handler
        canvas.safe_typer.status(self, exceptions, show_all_exceptions)
