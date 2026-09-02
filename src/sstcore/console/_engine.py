"""
Extend typer.Typer

- Provide Typer setup with Config, Log, EventBus and Error handling

"""

import sys
from typing import Unpack

import typer
from loguru import logger

from ..brick.view import view
from ..error.catch import ErrorRegistry
from ..port.system import CliSystemArgs, SstSystem
from ..system.boot import System, SystemLoader, sst_system_loader
from ..system.config import HomeSetup
from . import _args as args
from .cli import _scroll as scroll


@view.safe_typer  # ty:ignore
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
        def dispatcher(
            ctx: typer.Context,
            # AI: here is clear, args for typer, written out!
            verbose: args.Verbose = False,
            quiet: args.Quiet = False,
            settings: args.SettingFile = None,
            home: HomeSetup = HomeSetup.PROJECT,
        ):
            """Route and provide CLI args for Main app"""
            if ctx.parent is None:
                self._run_main_callback(
                    ctx,
                    verbose=verbose,
                    quiet=quiet,
                    settings=settings,
                    home=home,
                )
            else:
                self._run_sub_callback(ctx)

    def _run_main_callback(
        # AI: here is unclear, internal args by **cli_args fine?
        self,
        ctx: typer.Context,
        **cli_args: Unpack[CliSystemArgs],
    ):
        """Setup Config and Logging and show Status"""

        self.errors: ErrorRegistry = self._error_registry or ErrorRegistry()

        loader: SystemLoader = self._system_loader or sst_system_loader()
        self.system: SstSystem = loader(**cli_args)
        self._update_system_context(ctx)

        # LATER: update input scroll prints
        # if not quiet:  # TODO: send system! (emit!)
        #     scroll.safe_typer.intro(ctx.info_name)  # FIX: info_name
        #     # TASK: split quiet: scroll prints, subapps, general, ...
        #     scroll.safe_typer.setup(self.system.config, loader)

    def _update_system_context(
        self, ctx: typer.Context, system: SstSystem | None = None
    ) -> None:
        ctx.obj = ctx.obj or {}
        system: SstSystem = system or self.system
        system_context: dict = {
            "system": system,
            "config": system.config,
            "printer": system.printer,
            "bus": system.bus,
            "emitter": system.emitter,
        }
        ctx.obj.update(system_context)

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
