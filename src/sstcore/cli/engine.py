"""
Extend typer.Typer

- Read details in SafeTyper
"""

import sys
from collections.abc import Callable
from pathlib import Path

import typer
from loguru import logger

from ..config import ConfigManager
from ..config.loader import ConfigLoader, sst_config_loader
from ..events.core import EventSystem, SystemLoader, build_event_system
from ..utils.log import LogSetupResult, setup_logging
from ..utils.log.setup import setup_minimal_logging
from . import args, canvas

type ErrorType = type[BaseException]
type ErrorHandler = Callable[
    [BaseException], None  # NEXT: more than just BaseException?
]
type ErrorHandlerDict = dict[ErrorType, ErrorHandler]


class SafeTyper(typer.Typer):
    """
    Lead Custom Typer Setup with Config, Log and Error handling

    - Provide Framework with basic callback attach and start prints
    - Ensure Loguru is ready and loaded with custom settings
    - Protect CLI display from Errors with registered Exception handlers

    """  # TODO: text to system

    def __init__(
        self,
        config_loader: ConfigLoader | None = None,
        system_loader: SystemLoader | None = None,
        **kwargs,
    ):
        """Load Typer and prepare custom setup"""

        kwargs.setdefault("no_args_is_help", True)
        super().__init__(**kwargs)

        self._config_loader: ConfigLoader = config_loader or sst_config_loader
        self._error_handlers: ErrorHandlerDict = {}

        # AI_TASK: maybe system_loader replaces/includes config_loader?
        self._system_loader: SystemLoader = system_loader or build_event_system

        self._attach_internal_callback()

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

        # AI_QUESTION: how to attach this into EventSystem?
        # - is it even the right place or where to do the general setup?
        config: ConfigManager = self._config_loader(setting_file)
        # Wait for Printer until Injection in config_loader is done!

        log_result: LogSetupResult = setup_logging(
            log_level_override="DEBUG" if verbose else None,
            quiet=quiet,
            param=config.settings.log,
        )
        # AI_QUESTION: maybe the line below replaces rest of function above?
        self.event_system: EventSystem = self._system_loader()

        if not quiet:
            canvas.safe_typer.intro(project_name=ctx.info_name)
            canvas.safe_typer.setup(config, self._config_loader, log_result)

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

    def _run_sub_callback(self, ctx: typer.Context):
        """Print Nice subapp title"""
        canvas.safe_typer.sub_callback(ctx.info_name or "subapp")

    def print_setup_status(self, show_all_exceptions=False):
        """Print summary of status after assembly"""  # REFACTOR: maybe to... ?
        exceptions: list = self.exceptions_of_all_handler
        canvas.safe_typer.status(self, exceptions, show_all_exceptions)

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

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ###  ERROR Handler
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    @property
    def n_handler(self) -> int:
        return len(self._error_handlers)

    @property
    def exceptions_of_all_handler(self) -> list[ErrorType]:
        """List Exception class of all registred handler"""
        return list(self._error_handlers.keys())

    def register_error_handler(self, exception: ErrorType):
        """Decorator: Attach Exception with custom Handler to Registry"""

        # TODO: improve type, why attach Exception basically twice?
        # @app.register_error_handler(TuiSelectorError)
        # def handle_tui_selector(error: TuiSelectorError):
        #     printer.danger(f"Selector failed: {error}")
        # - use that handler always has first (or even single) argument:
        # - error:Exception, grab this

        def decorator(handler: ErrorHandler):
            self._error_handlers[exception] = handler
            return handler

        return decorator

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ###  EVENT Handler
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def set_event_system_factory(  # NEXT: check if needed, how to modify
        self, factory: Callable[[ConfigManager], EventSystem]
    ):
        # AI: this was one idea, might be to slow for the main callback?
        """Allow projects to provide a custom EventSystem builder (like config_loader)."""
        self._event_system_factory = factory
        return factory  # decorator friendly
