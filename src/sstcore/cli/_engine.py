"""
Extend typer.Typer

- Provide Typer setup with Config, Log, EventBus and Error handling

"""

import sys
from pathlib import Path

import typer
from loguru import logger

from ..config import HomeSetup
from ..error.handler import ErrorRegistry
from ..port.system import CliSystem
from ..system.boot import System, SystemLoader, sst_system_loader
from ..utils.view import view
from . import _args as args
from . import _scroll as scroll


@view.safe_typer
class SafeTyper(typer.Typer):
    """
    Lead CLI execution and distribute bootstrapped System

    - Provide Framework with callback dispatch and scroll prints
    - Prepare System with EventBus for main app
    - Load Config from json or provide Defaults
    - Ensure Loguru is ready and loaded with custom settings
    - Register ErrorHandler and protect CLI display from spam

    """

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
        self._error_registry: ErrorRegistry | None = error_registry

        self._attach_internal_callback()

    def _attach_internal_callback(self):
        """Dispatch callback for Main or Subapp"""

        @self.callback()
        def dispatcher(  # NEXT: check args
            ctx: typer.Context,
            verbose: args.Verbose = False,
            quiet: args.Quiet = False,
            settings: args.SettingFile = None,
            home: HomeSetup = HomeSetup.PROJECT,
        ):
            """Route and provide CLI args for Main app"""
            if ctx.parent is None:
                self._run_main_callback(ctx, verbose, quiet, settings, home)
            else:
                self._run_sub_callback(ctx)

    def _run_main_callback(
        self,
        ctx: typer.Context,
        verbose: bool,
        quiet: bool,
        settings: Path | None,
        home: HomeSetup = HomeSetup.PROJECT,
    ):
        """Setup Config and Logging and show Status"""

        self.errors: ErrorRegistry = self._error_registry or ErrorRegistry()

        # NEXT: system_loader
        loader: SystemLoader = self._system_loader or sst_system_loader()
        self.system: CliSystem = loader(
            verbose=verbose, quiet=quiet, settings=settings, home=home
        )
        # IDEA: small helper for this update?
        ctx.obj = ctx.obj or {}
        ctx.obj.update(
            {
                "system": self.system,
                "config": self.system.config,
                "printer": self.system.printer,
                "bus": self.system.bus,
                "emitter": self.system.emitter,
            }
        )
        if not quiet:  # TODO: send system! (emit!)
            # NEXT: split quiet: scroll prints, subapps, general, ...
            scroll.safe_typer.intro(
                project_name=ctx.info_name
            )  # FIX: info_name
            scroll.safe_typer.setup(self.system.config, loader)

    def _run_sub_callback(self, ctx: typer.Context):
        """Print Nice subapp title"""
        # LATER: what about Error Handler in subapps?
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
