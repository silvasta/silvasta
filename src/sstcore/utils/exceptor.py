"""
Exceptor - Massivly load and launch exceptions

- app: Launch setup inside Typer application
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import typer

from sstcore import printer
from sstcore.utils.paint import ColorBox

c: ColorBox = ColorBox.with_mode("bold")


type ErrorHandler = Callable[[Any], None]

type ErrorList = list[type[BaseException] | ExceptorTask]


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
        task: str = c.yellow(type(self).__name__)
        error: str = c.red(self.error.__name__)
        args: str = f"  {c.b('args')}    {self.args or 'not loaded'}"
        kwargs: str = f"  {c.b('kwargs')}  {self.kwargs or 'not loaded'}"
        _handler: str = c.blue(self.handler.__name__) if self.handler else ""  # ty:ignore
        handler: str = f"  {c.magenta('handler')} {_handler or 'not loaded'}"
        return f"  {task} {error}\n{args}\n{kwargs}\n{handler}"

        # HACK: check what here is going  wrong... it always strips the left side just away
        # args = f"{c.b('args'):10} {self.args or 'not loaded'}"
        # kwargs = f"{c.b('kwargs'):10} {self.kwargs or 'not loaded'}"
        # handler = f"{c.b('handler'):10} {self.handler or 'not loaded'}"

    def __call__(self):
        """Dispatch args and kwargs then Raise"""

        match (self.args is None, self.kwargs is None):
            case (True, True):
                raise self.error

            case (False, True):
                raise self.error(*self.args)  # ty:ignore

            case (True, False):
                raise self.error(**self.kwargs)  # ty:ignore

            case (False, False):
                raise self.error(*self.args, **self.kwargs)  # ty:ignore

        printer.special(f"{c('Fail at load kw|arg!', 'purple')} {self}!")

    @classmethod
    def ensure_list(cls, tasks: ErrorList) -> list[ExceptorTask]:
        return [
            item  # Just Forward already prepared Tasks
            if isinstance(item, ExceptorTask)
            else cls(item)
            for item in tasks
        ]


class NoTyperLoadedError(AttributeError):  # LATER: __rich__ example
    """Raise if Typer is Launched but not Loaded"""


class Exceptor:
    """Show console output and handling of attached Exceptions"""

    app: typer.Typer | None = None
    quiet = False  # used for Typer setup

    @property
    def with_typer(self) -> bool:
        return self.app is not None

    def __init__(
        self, tasks: ErrorList, app: typer.Typer | None = None, direct=True
    ):
        self.tasks: list[ExceptorTask] = ExceptorTask.ensure_list(tasks)
        if app:
            self._load_typer(app)
        if direct:
            self()

    def __str__(self) -> str:
        return "Exceptor is launching..."

    def __repr__(self) -> str:
        with_app: str = "::WithTyper" if self.with_typer else ""
        return f"Exceptor{with_app}({self.tasks})"

    def __rich__(self) -> str:
        return f"{c.s(Exceptor)} {c.red('is launching')}..."

    def __call__(self):
        printer.warn(f"{self}")

        for task in self.tasks:
            printer.header(f"{c.cyan('Next')} {task}")
            printer(task)

            if self.with_typer:
                self._raise_typer(task)
            else:
                self._raise_exception(task)

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Typer
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def _load_typer(self, app: typer.Typer):
        @app.command()
        def throw():
            self._current_task()

        self.app: typer.Typer = app

        app_name: str = type(self.app).__name__
        printer.header(f"{app_name} Loaded: {app}")

    def _raise_typer(self, task: ExceptorTask):
        app_name: str = type(self.app).__name__
        try:
            self._current_task: ExceptorTask = task
            with printer.muted():
                self.app(["throw"], standalone_mode=False)  # ty:ignore
            printer.success(f"{c.g(app_name)} catched the Error")
        except NoTyperLoadedError:
            printer.danger(f"Provide proper Typer! Ignoring: {task}")

        except BaseException as error:
            printer.danger(f"{c.r(app_name)} crashed: {error=}")

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Regular Exectuion
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def _raise_exception(self, task: ExceptorTask):
        try:
            task()  # load arg and kwarg from dataclass

        except BaseException as error:
            _error = str(error) or f"{error!r}"
            printer.danger(f"{c.r('Error Detected')} {_error}")
            if task.handler:
                try:
                    task.handler(error)
                    printer.success("Error Handler complete!")

                except BaseException as handler_fail:
                    printer.danger("Error Handler Failed!")
                    printer(handler_fail)

            printer(c.c(f"  Finish {task}\n", color="dim italic"))
