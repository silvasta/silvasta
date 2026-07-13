"""
Extend typer.Typer

(Read details in SafeTyper)
"""

import sys
from pathlib import Path

import typer
from loguru import logger
from typer import Context

from ..config.setup import ConfigLoader, sst_config_loader
from ..system.core import System, fetch_system
from . import args, canvas
from .handler import ErrorRegistry


def get_system(ctx: Context) -> System:
    if isinstance(ctx.obj, dict) and "system" in ctx.obj:
        return ctx.obj["system"]
    return fetch_system(_allow_uninitialized=True)


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
        error_registry: ErrorRegistry | None = None,
        **kwargs,
    ):
        """Load Typer and prepare custom setup"""

        kwargs.setdefault("no_args_is_help", True)
        super().__init__(**kwargs)

        self.errors: ErrorRegistry = error_registry or ErrorRegistry()
        self.system: System | None = None

        self._config_loader: ConfigLoader = config_loader or sst_config_loader

        self._attach_internal_callback()

    def _run_main_callback(
        self,
        ctx: typer.Context,
        verbose: bool,
        quiet: bool,
        setting_file: Path | None,
    ):
        """Setup Config and Logging and show Status"""

        system: System = System.bootstrap(
            config_loader=self._config_loader,
            setting_file=setting_file,
            verbose=verbose,
            quiet=quiet,
        )
        self.system: System = system

        ctx.obj = ctx.obj or {}
        ctx.obj["system"] = system
        ctx.obj["config"] = system.config
        ctx.obj["printer"] = system.printer
        ctx.obj["bus"] = system.bus

        if not quiet:
            canvas.safe_typer.intro(project_name=ctx.info_name)
            canvas.safe_typer.setup(
                system.config,  # TODO: send system! (emit!)
                self._config_loader,
                system.config.log_result,
            )

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
                handler.execute_safe(error)  # -> NoReturn!
                # LATER: check __mro__ for derived exceptions!

            # Fallback for unhandled structural issues
            logger.exception("CLI Execution: Critical Failure...")
            sys.exit(1)
