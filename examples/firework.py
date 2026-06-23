from pathlib import Path

import fire

from sstcore import printer
from sstcore.cli.engine import SafeTyper
from sstcore.exceptions import (
    NotImplementedDispatchError,
    RegistrySyncError,
    SstError,
    TuiSelectorError,
)
from sstcore.utils.exceptor import (
    ErrorList,
    Exceptor,
    ExceptorTask,
    ExceptorTaskHandler,
)


def main() -> None:
    fire.Fire(ExceptorLaunch)


class ExceptorLaunch:
    def list(self):
        Exceptor(all_tasks)

    def app(self):
        Exceptor(all_tasks, app)

    def delay(self):
        exceptor = Exceptor(all_tasks, app, direct=False)
        printer(exceptor)
        input("ENTER")
        exceptor()

    def task(self):
        for task in [*exceptor_tasks, handled_task]:
            printer.header(f"Launch from CLI: {task}")
            printer(task)
            printer(f"{task=}")

    def error(self):
        tasks: list[ExceptorTask] = ExceptorTaskHandler.ensure(internal)
        for task in tasks:
            printer.line()
            printer(task)
            printer(task.load())

            printer.box("the new box")
            printer.box_bottom("the new bottom")
            printer.box_top("the new top")


app = SafeTyper(
    name="error_test",
    help="Attach ExceptionHandler and send trough Exceptor",
)


@app.register_error_handler(TuiSelectorError)
def handle_tui_selector(error: TuiSelectorError):
    printer.danger(f"Selector failed: {error}")


class MissingFileError(FileNotFoundError):
    def __init__(self, path: Path):
        self.path: Path = path

    def __str__(self):
        return type(self).__name__


@app.register_error_handler(MissingFileError)
def handle_missing_file(error: MissingFileError):
    scroll: list[str] = [
        f"  Start of handling: {error}",
        f"  observing path: {error.path}",
        f"  sending message to {printer.colors.yellow('DataManager')}...",
    ]
    printer(scroll)
    printer.green("  Handle Missing Path completed")


handled_task = ExceptorTask(
    error=MissingFileError,
    args=(Path("/home/silvan/here/failed/the/path/to_file.py"),),
    handler=handle_missing_file,
)

internal: ErrorList = [
    SstError,
    RegistrySyncError,
    ExceptorTask(
        error=NotImplementedDispatchError,
        args=("hello", 11),
        kwargs={"test": 112},
    ),
]
tasks: ErrorList = [
    TuiSelectorError,
    KeyboardInterrupt,
    handled_task,
]

exceptor_tasks: list[ExceptorTask] = [
    ExceptorTask(error=SstError),
    ExceptorTask(
        error=SstError,
        args=("hello", 11),
    ),
    ExceptorTask(
        error=NotImplementedDispatchError,
        args=("hello", 11),
        kwargs={"test": 112},
    ),
]

all_tasks: ErrorList = tasks + exceptor_tasks


if __name__ == "__main__":
    main()
