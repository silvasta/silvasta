"""
Extend typer.Typer

- Read details in SafeTyper
"""

import sys
from pathlib import Path

import typer
from loguru import logger

from ..config import ConfigManager
from ..config.loader import ConfigLoader, sst_config_loader
from ..events.core import EventSystem, SystemLoader, build_event_system
from ..utils.log import LogSetupResult, setup_logging
from ..utils.log.setup import setup_minimal_logging
from . import args, canvas
from .handler import ErrorRegistry


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
        error_registry: ErrorRegistry | None = None,
        **kwargs,
    ):
        """Load Typer and prepare custom setup"""

        kwargs.setdefault("no_args_is_help", True)
        super().__init__(**kwargs)

        self.errors: ErrorRegistry = error_registry or ErrorRegistry()

        self._config_loader: ConfigLoader = config_loader or sst_config_loader
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
        """Print summary of status after assembly"""
        canvas.safe_typer.status(self, self.errors.all, show_all_exceptions)

    def __call__(self, *args, **kwargs):
        """Run Typer app as usual but intercept critical Errors"""
        try:
            return super().__call__(*args, **kwargs)

        except Exception as error:
            if handler := self.errors.get(exception_type=type(error)):
                # LATER: check __mro__ for derived exceptions!
                handler.execute_safe(error)  # -> NoReturn!

            # Fallback for unhandled structural issues
            logger.exception("CLI Execution: Critical Failure...")
            sys.exit(1)
