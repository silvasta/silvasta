import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import typer
from loguru import logger

from ..config import ConfigManager
from ..config.loader import default_config_loader
from ..utils import printer
from ..utils.log import LogSetupResult, setup_logging
from ..utils.log.setup import setup_minimal_logging
from . import args, canvas

type ErrorHandlerDict = dict[type[BaseException], Callable[[Any], None]]
type ConfigLoader = Callable[[Path | None], ConfigManager]


class SafeTyper(typer.Typer):
    """
    Lead Custom Setup for Typer App with Log and Error handling

    - Provide Framework with basic callback attach and start prints
    - Ensure Loguru is ready and loaded with custom settings
    - Protect CLI display from Errors with registered Exception handlers

    """

    def __init__(self, config_loader: ConfigLoader | None = None, **kwargs):
        kwargs.setdefault("no_args_is_help", True)
        super().__init__(**kwargs)

        # TODO: avoid like 5 logs in console when multiple subapps are attached
        # if config_loader: # with this only 1, but maybe 0 needed?
        #     logger.info(f"Start of Setup: {type(self).__name__}")

        self._config_loader: ConfigLoader | None = config_loader
        self._error_handlers: ErrorHandlerDict = {}
        self._attach_internal_callback()

    def register_error(self, exception: type[BaseException]):
        """Decorator: Attach Exception with custom Handler to Registry"""

        # TODO: check for better typing

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

            # Fallback for unhandled structural issues
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

        setup_minimal_logging("DEBUG" if verbose else "WARNING")

        load_from_default: bool = self._config_loader is None

        config: ConfigManager = (  # IDEA: attach to typer context?
            default_config_loader(setting_file)
            if load_from_default
            else self._config_loader(setting_file)
        )
        # Move after config, waiting for Printer injection in config setup
        printer.title(f"Welcome to {ctx.info_name}!")
        printer.header("Setup Config and Logging")

        canvas.main_callback_config_setup(config, load_from_default)

        result: LogSetupResult = setup_logging(
            log_level_override="DEBUG" if verbose else None,
            quiet=quiet,
            param=config.settings.log,
        )
        canvas.main_callback_log_setup(result)

    def _run_sub_callback(self, ctx: typer.Context):
        """Print Nice Title for launching Subapp"""
        printer.title(f"Launching attached App: {ctx.info_name}!")
