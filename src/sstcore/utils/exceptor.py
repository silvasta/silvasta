"""
Exceptor - Massivly load and launch exceptions

- app: Provide Environment and Tracking for Exectuion inside Typer Setup

"""

import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Self

from sstcore import printer
from sstcore.cli.engine import SafeTyper  # WARN: this worked before, but...
from sstcore.utils.color import ColorBox

c: ColorBox = ColorBox.bold()


type ErrorHandler = Callable[[Any], None]
type ErrorList = list[type[BaseException] | ExceptorTask]

# TODO: check with latest __fmt__

# MOVE: maybe to CLI, together with other utils, tools


@dataclass
class ExceptorTaskHandler:
    """Manage ExceptorTask Collection"""

    registry: list[ExceptorTask] = field(default_factory=list)

    # LATER: extend general global property setup

    @property
    def all_exceptions(self) -> ErrorList:
        return [task.error for task in self.registry]

    @classmethod
    def arise(cls, tasks: ErrorList) -> Self:
        """Arise from the confirmed List of given Task and Exceptions"""
        ensured_tasks: list[ExceptorTask] = [
            item  # just forward already prepared tasks
            if isinstance(item, ExceptorTask)
            else ExceptorTask(item)
            for item in tasks
        ]
        return cls(ensured_tasks)

    @classmethod
    def ensure(cls, tasks: ErrorList) -> list[ExceptorTask]:
        """Confirm List and provide valid ExceptorTasks"""
        return cls.arise(tasks).registry


class Exceptor:
    """Raise one Exception after another and show Nice CLI and Clear Debug"""

    app: SafeTyper | None = None
    quiet = False  # used to silence SafeTyper log setup in sstcore

    @property
    def has_typer(self) -> bool:
        return isinstance(self.app, SafeTyper)

    def __init__(
        self,
        tasks: ErrorList,
        app: SafeTyper | None = None,
        direct: bool = True,
    ):
        self.tasks: list[ExceptorTask] = ExceptorTaskHandler.ensure(tasks)
        if app:
            self.app: SafeTyper = app
            self._load_typer()
        direct and self()  # risky but this is as well a fun tool

    def __call__(self):
        printer.line()
        printer.box(self)

        for task in self.tasks:
            printer.box(f"{c.cyan('Next')} {task}")
            printer(task.error)
            printer(task)

            if self.has_typer:
                self._raise_typer(task)
            else:
                self._raise_exception(task)

            printer(c(f"  Finished {task}\n", color="dim italic"))

    # NEXT: here Exceptor
    def __rich__(self) -> str:
        return f"{c.c(type(self).__name__)} {'Start of Launch'}..."

    def __str__(self) -> str:
        return "Exceptor is launching..."

    def __repr__(self) -> str:
        with_app: str = "::WithTyper" if self.has_typer else ""
        return f"Exceptor{with_app}({self.tasks})"

    # ------------------------------------------------------------------ #
    # SafeTyper Integration
    # ------------------------------------------------------------------ #

    def _load_typer(self):

        if not isinstance(self.app, SafeTyper):
            warn: str = c.yellow("Provided app is not SafeTyper")
            printer.warn(warn + " – falling back to raw mode")
            return

        @self.app.command()
        def throw():
            self._current_task()

        n_handler: int = self.app.errors.n_handler
        n_tasks: int = len(self.tasks)

        printer.header(f"{self.app} {n_handler=} for {n_tasks=}")

    def _raise_typer(self, task: ExceptorTask):
        assert isinstance(self.app, SafeTyper)

        self._current_task: ExceptorTask = task
        try:
            with printer.muted():  # silence print, no catch executed here!
                self.app(["throw"], standalone_mode=False)
            printer.success(f"{c.g(self.app)} catched the Error")

        except SystemExit:
            printer.yellow(f"{c.y(self.app)} triggered sys.exit(1)")

        except BaseException as error:
            _error: str = type(error).__name__
            critical_end: str = c.r("CLI Execution: Critical Failure...")
            printer.danger(f"{c.r(self.app)} {critical_end}")

            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                printer.warn(f"System exception {c.r(_error)} received")

    # ------------------------------------------------------------------ #
    ### Regular Exectuion
    # ------------------------------------------------------------------ #

    def _raise_exception(self, task: ExceptorTask):
        try:
            task()  # load arg and kwarg from dataclass

        except BaseException as error:
            _error = str(error) or f"{error!r}"
            # printer.danger(f"{c.r('Error Detected')} {_error}")
            printer.dip(head="Error Detected", text=_error, color="red")

            if task.handler:
                try:
                    task.handler(error)
                    printer.success("Error Handler complete!")

                except BaseException as handler_fail:
                    printer.danger("Error Handler Failed!")
                    printer(handler_fail)


@dataclass
class ExceptorTask:
    """Provide Input and Handler with Exception and Raise"""

    error: type[BaseException]
    args: tuple[Any, ...] | None = None
    kwargs: dict[str, Any] | None = None
    handler: ErrorHandler | None = None

    def __str__(self):
        return f"{type(self).__name__}::{self.error.__name__}"

    def __rich__(self):
        # REFACTOR: compare with latest status of Exception Panel
        task: str = c.yellow(type(self).__name__)
        error: str = c.red(self.error.__name__)
        args: str = f"  {c.c('args')}    {self.args or 'not loaded'}"
        kwargs: str = f"  {c.c('kwargs')}  {self.kwargs or 'not loaded'}"
        _handler: str = c.clue(self.handler.__name__) if self.handler else ""  # ty:ignore
        handler: str = f"  {c.magenta('handler')} {_handler or 'not loaded'}"
        return f"  {task} {error}\n{args}\n{kwargs}\n{handler}"

        # HACK: check later what here is going  wrong...
        # - it always strips the left side just away
        # - ...most likely one of the Printer.format issues
        # args = f"{c.c('args'):10} {self.args or 'not loaded'}"
        # kwargs = f"{c.c('kwargs'):10} {self.kwargs or 'not loaded'}"
        # handler = f"{c.c('handler'):10} {self.handler or 'not loaded'}"

    def __call__(self):
        """Dispatch args and kwargs then Raise"""
        printer(exception := self.load())

        raise exception

    def load(self) -> BaseException:

        match (self.args is None, self.kwargs is None):
            case (True, True):
                return self.error()

            case (False, True):
                return self.error(*self.args)  # ty:ignore

            case (True, False):
                return self.error(**self.kwargs)  # ty:ignore

            case (False, False):
                return self.error(*self.args, **self.kwargs)  # ty:ignore

        arguments: str = f"{c.c('args')} and {c.c('kwargs')}"
        printer.special(f"{c.purple(self)} Failed to load {arguments}!")
        return sys.exit(2)
