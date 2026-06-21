from pathlib import Path

import fire

from sstcore import printer
from sstcore.cli.engine import SafeTyper
from sstcore.exceptions import (
    NotImplementedDispatchError,
    SstError,
    TuiSelectorError,
)
from sstcore.utils.exceptor import ErrorList, Exceptor, ExceptorTask


def handle_missing_file(error: FileMissingFoundError):
    scroll: list[str] = [
        f"  Start of handling: {error}",
        f"  observing path: {error.path}",
        f"  sending message to {printer.colors.yellow('DataManager')}...",
    ]
    printer(scroll)
    printer.green("  Handle Missing Path completed")


class FileMissingFoundError(FileNotFoundError):
    def __init__(self, path: Path):
        self.path: Path = path

    def __str__(self):
        return type(self).__name__


handled_task = ExceptorTask(
    error=FileMissingFoundError,
    args=(Path("/home/silvan/here/failed/the/path/to_file.py"),),
    handler=handle_missing_file,
)


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
        error=SstError,
        kwargs={"test": 112},
    ),
    ExceptorTask(
        error=NotImplementedDispatchError,
        args=("hello", 11),
        kwargs={"test": 112},
    ),
]

# all_tasks: ErrorList = tasks + exceptor_tasks
all_tasks: ErrorList = [handled_task]


def main() -> None:
    printer.title("Launching Exceptor")
    fire.Fire(ExceptorLaunch)


class ExceptorLaunch:
    def list(self):
        Exceptor(all_tasks)

    def app(self):
        Exceptor(tasks, app)

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


app = SafeTyper(
    name="error_test",
    help="Attach ExceptionHandler and send trough Exceptor",
)


@app.register_error_handler(TuiSelectorError)
def handle_tui_selector(error: TuiSelectorError):
    printer.danger(f"Selector failed: {error}")


if __name__ == "__main__":
    main()
