"""Use printer to paint SafeTyper"""

import random
from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum, auto

from sstcore.utils.print.mixin._boxes import BoxLibrary

from ...config import ConfigManager
from ...utils import printer
from ...utils.color import ColorBox
from ...utils.log import LogSetupResult
from . import _random  # REMOVE: when migrated

c: ColorBox = ColorBox.bold()

# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###  SafeTyper
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


# NOTE: Idea 1: pure function
def intro(project_name):
    printer.title(  # TODO: select version
        c.cyan(f"Welcome to {c.white(project_name)}")
        if random.getrandbits(1)
        else c.white(f"Welcome to {c.cyan(project_name)}"),
        box=BoxLibrary().EDGE,
    )
    printer.box_mini("Setup Config and Log", mode=_random.mode_1)


# NOTE: Idea 2: dataclass
@dataclass
class ConfigSetup:
    config: ConfigManager
    loader_func: Callable

    def __call__(self):
        """Visualize Config setup"""

        project, *modules = self.loader_func.__module__.split(".")
        # LATER: test: module: str = ".".join([c.c(project), *[c.g(m) for m in modules]])
        module: str = ".".join([c.cyan(project), *modules])
        loader = f"{c.white(self.loader_func.__name__)}"  # ty:ignore

        text: str = f"{c.cyan(self.config)} loaded via {module}::{loader}"

        printer.box_mini(text, mode=_random.mode_2)

        config_title = f"{c.blue('Config')} "
        _log_and_config_file(self.config.setting_file, title=config_title)


# REMOVE: after selection
_log_and_config_file_dispatch: int = random.getrandbits(2)


def _log_and_config_file(path, title):
    """Print log and config path in 'team' style"""

    # NOTE: baseline (so far as well ruptive changes in printer)
    # printer.title(path, title=title, frame="blue")

    if _log_and_config_file_dispatch > 1:
        frame = "blue"
    else:
        frame = "white"
    if _log_and_config_file_dispatch % 2 == 0:
        box = BoxLibrary().EDGE
    else:
        box = BoxLibrary().OPEN

    printer.title(path, title=title, frame=frame, box=box)


# NOTE: Idea 1: pure function
def main_callback_log_setup(result: LogSetupResult):
    """Visualize Log setup"""

    if result.print_at_setup:
        printer(result)

    if result.log_file:
        log_title = f"{c.blue('Log')} "
        _log_and_config_file(result.log_file, title=log_title)
    else:
        printer.dip("LogFile", "No setup active for tracking Events", "yellow")


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Status
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


# NOTE: Idea 3: direct fire class with simple facade but strong dispatch contol


class Status:  # AI: something like this for main_callback could work well
    def __init__(self, safe, exceptions, show_handler):
        """Provide the central theme for the execution"""

        # NOTE: here or by arg/injection will be the selection
        self.ready.for_execution(safe)

        printer(f"Attached {len(exceptions)} Error Handler", _i=2)

        if show_handler:
            printer(self.format.on_list(exceptions), _i=4)

        printer("Some statistics: ...", _i=2)
        printer.line("yellow")

        # NOTE: end of execution And instance

    class Ready(IntEnum):
        DEFAULT = auto()
        TEST_WITH_BOX = auto()

        # AI: this will grow sometimes or collapse, overall it will change rare
        # - this could be like the perfect design status governour

        def for_execution(self, safe):
            return [
                _ready_for_execution,
                _ready_for_execution_new_box,
            ][self - 1](safe)

        # IDEA:
        # - def launch_all(...
        # - def launch_random(...

    class Format(IntEnum):
        RAW = auto()
        COLORFUL = auto()

        def on_list(self, exceptions) -> list:
            _format = [
                _format_raw,
                _format_colorful,
            ][self - 1]
            return [_format(e) for e in exceptions]

    ready: Ready = Ready.DEFAULT
    # AI: parameter around almost never controlled by cli,
    # either by random selector while design choice,
    # or by programmer directly here, just as develop support
    format: Format = Format.COLORFUL


# AI: this around could be attached but space for prints is highly valuable 79.

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Ready
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def _ready_for_execution_new_box(safe):
    printer.box_full(f"{c.y(safe)} Ready for Execution", frame="yellow")
    printer("remove later on...", _i=4)


def _ready_for_execution(safe):
    printer.box(f"{c.y(safe)} Ready for Execution", frame="yellow")


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Format
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def _format_raw(exception: type[BaseException]):
    return exception


def _format_colorful(exception: type[BaseException]):
    # MOVE: project/module to generic? check similar in: main_callback_config_setup
    project, *modules = exception.__module__.split(".")
    module: str = ".".join([c.c(project), *[c.g(m) for m in modules]])
    error = f"{c.red(exception.__name__)}"
    return f"{module}.{error}"
