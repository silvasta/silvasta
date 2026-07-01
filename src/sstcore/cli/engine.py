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
        # - use that handler has always first (or even all) arguments like:
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

            # INFO:Fallback for unhandled structural issues
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

        config: ConfigManager = self._config_loader(setting_file)
        # Wait for Printer until Injection in config_loader!

        result: LogSetupResult = setup_logging(
            log_level_override="DEBUG" if verbose else None,
            quiet=quiet,
            param=config.settings.log,
        )
        if not quiet:
            canvas.safe_typer.intro(project_name=ctx.info_name)
            canvas.safe_typer.ConfigSetup(config, self._config_loader)()
            canvas.safe_typer.main_callback_log_setup(result)

    def _run_sub_callback(self, ctx: typer.Context):
        """Print Nice subapp title"""
        # MOVE: canvas
        # NEXT:
        # NEXT:
        # NEXT:
        printer.title(f"Launching attached App: {ctx.info_name}!")

    def print_setup_status(self, show_handler=False):
        """Launch Summary of Status after assembly"""
        exceptions: list = self.exceptions_of_all_handler
        canvas.safe_typer.Status(self, exceptions, show_handler)
