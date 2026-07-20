"""
Extend typer.Typer

(Read details in SafeTyper)
"""

import sys
from pathlib import Path

import typer
from loguru import logger

from ..system.core import System, SystemLoader, sst_system_loader
from ..utils.path import HomeSetup
from ..utils.view import presets, view
from . import args, scroll
from .handler import ErrorRegistry


@view(spec=presets.safe_typer_view_builder())
class SafeTyper(typer.Typer):
    """
    Lead Custom Typer Setup with Config, Log and Error handling

    - Provide Framework with basic callback attach and start prints
    - Ensure Loguru is ready and loaded with custom settings
    - Protect CLI display from Errors with registered Exception handlers

    """  # TODO: text to system

    system: System
    errors: ErrorRegistry

    def __init__(
        self,
        system_loader: SystemLoader | None = None,
        error_registry: ErrorRegistry | None = None,
        **kwargs,
    ):
        """Load Typer and prepare custom setup"""

        kwargs.setdefault("no_args_is_help", True)
        super().__init__(**kwargs)

        self._system_loader: SystemLoader | None = system_loader
        self.errors: ErrorRegistry = error_registry or ErrorRegistry()

        self._attach_internal_callback()

    def _run_main_callback(
        self,
        ctx: typer.Context,
        verbose: bool,
        quiet: bool,
        setting_file: Path | None,
        home: HomeSetup = HomeSetup.PROJECT,
    ):
        """Setup Config and Logging and show Status"""

        loader: SystemLoader = self._system_loader or sst_system_loader()

        self.system: System = loader(
            verbose=verbose,
            quiet=quiet,
            setting_file=setting_file,
            home=home,
        )
        ctx.obj = ctx.obj or {}
        ctx.obj.update(
            {
                "system": self.system,
                "config": self.system.config,
                "printer": self.system.printer,
                "bus": self.system.bus,
            }
        )

        if not quiet:
            scroll.safe_typer.intro(project_name=ctx.info_name)
            scroll.safe_typer.setup(
                self.system.config,  # TODO: send system! (emit!)
                loader,
                self.system.config.log_result,
            )

    def _attach_internal_callback(self):
        """Dispatch callback for Main or Subapp"""

        @self.callback()
        def dispatcher(
            ctx: typer.Context,
            verbose: args.Verbose = False,
            quiet: args.Quiet = False,
            setting_file: args.SettingFile = None,
            home: HomeSetup = HomeSetup.PROJECT,
        ):
            if ctx.parent is None:
                self._run_main_callback(
                    ctx, verbose, quiet, setting_file, home
                )
            else:
                self._run_sub_callback(ctx)

    def _run_sub_callback(self, ctx: typer.Context):
        """Print Nice subapp title"""
        scroll.safe_typer.sub_callback(ctx.info_name or "subapp")

    def print_setup_status(self, show_all_exceptions=False):
        """Print summary of status after assembly"""
        scroll.safe_typer.status(self, self.errors.all, show_all_exceptions)

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
