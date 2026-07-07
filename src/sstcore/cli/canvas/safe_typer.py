"""
Assemble the Prints for SafeTyper

- Handle complexity here and just provide a simple Canvas
- Use PrintOptions to display different layouts and ideas
  - for now: with easy toggle to final selection
  - in future: connected and reacting to app state
"""

from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any, Literal

from rich.box import Box

from sstcore.utils.color.palette import ColorName
from sstcore.utils.print.mixin._boxes import BoxLibrary

from ...config import ConfigManager
from ...config.loader import ConfigLoader
from ...utils import printer
from ...utils.color import ColorBox, colorize
from ...utils.log import LogSetupResult
from .option import PrintOption, SelectMode

c: ColorBox = ColorBox.bold()
boxes = BoxLibrary()


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###  Intro
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class MainIntroCanvas(PrintOption[Callable[[str], None]]):
    def _load_default_function(self):
        return partial(
            self._template, outer="white", inner="cyan", box=boxes.OPEN
        )

    def _template(
        self, project_name: str, outer: ColorName, inner: ColorName, box: Box
    ) -> None:
        project: str = c(project_name, color=inner)

        text: str = c(f"Welcome to {project}", color=outer)

        printer.title(text, box=box, frame="cyan")

    def _set_more_if_desired(self):
        param_grid: dict[str, Any] = {
            "box": [boxes.OPEN, boxes.EDGE],
        }
        kwargs: dict[str, str] = {"outer": "white", "inner": "cyan"}
        self.grid(self._template, param_grid, common_kwargs=kwargs)


intro = MainIntroCanvas(select_mode=SelectMode.RANDOM)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###  setup
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


type Mode = Literal["up", "both", "down"]

type ConfigSignature = Callable[[ConfigManager, ConfigLoader], None]
type LoaderStyler = Callable[[ConfigLoader], str]


class ConfigLoaderCanvas(PrintOption[ConfigSignature]):
    def _load_default_function(self):
        styler: LoaderStyler = colorize.module_path
        return partial(self._template, mode="both", styler=styler)

    def _template(
        self,
        config: ConfigManager,
        loader: ConfigLoader,
        styler: LoaderStyler,
        mode: Mode,
    ) -> None:
        _config: str = c.cyan(config)
        _loader: str = styler(loader)

        text: str = f"{_config} loaded via {_loader}"

        printer.mini_box(text, mode=mode)

    def _set_more_if_desired(self):
        self.register(self._config_module_path_1(mode="both"))
        self.register(_config_module_path_2)

    def _config_module_path_1(self, mode: Mode):
        styler: LoaderStyler = partial(
            colorize.module_path,
            project_color="purple",
            module_color="green",
            target_color="cyan",
        )
        return partial(self._template, mode=mode, styler=styler)

    def _param_grid(self):  # NOTE: unused at moment, Mode "both" best so far
        param_grid: dict[str, list[Mode]] = {
            "mode": ["up", "both", "down"],
        }
        self.grid(self._template, param_grid=param_grid)


def _config_module_path_2(config: ConfigManager, loader: ConfigLoader) -> None:
    # MOVE: do stuff like this in colorize
    project, *modules = loader.__module__.split(".")
    module: str = ".".join([c.cyan(project), *modules])
    _loader = f"{c.white(getattr(loader, '__name__', 'loader_func'))}"
    text: str = f"{c.cyan(config)} loaded via {module}::{loader}"
    printer.mini_box(text, mode="both")


type PathSignature = Callable[[Path, Literal["log", "config"]], None]


class ConfigAndLogPanel(PrintOption[PathSignature]):
    """Create Log and Config path in same style"""

    def _load_default_function(self):
        return partial(self._template, frame="blue", box=None)

    def _template(
        self,
        path: Path,
        mode: Literal["log", "config"],
        frame: str = "blue",
        box: Box | None = boxes.EDGE,
    ):
        table: dict[str, str] = {
            "log": f"{c.blue('Log')} ",
            "config": f"{c.blue('Config')} ",
        }
        _box = {} if box is None else {"box": box}

        printer.title(path, title=table[mode], frame=frame, **_box)

    def _set_more_if_desired(self):
        param_grid: dict[str, Any] = {
            "box": [boxes.OPEN, boxes.EDGE, None],
            "frame": ["white", "blue"],
        }
        self.grid(self._template, param_grid=param_grid)


config_loader = ConfigLoaderCanvas(select_mode=SelectMode.RANDOM)
log_or_config_path = ConfigAndLogPanel(select_mode=SelectMode.RANDOM)


def setup(config: ConfigManager, loader: Callable, log_result: LogSetupResult):
    """Provide main callback text"""

    config_loader(config, loader)
    log_or_config_path(config.setting_file, mode="config")

    if log_result.print_at_setup:
        printer(log_result)

    if log_result.log_file:
        log_or_config_path(log_result.log_file, mode="log")
    else:
        printer.dip("LogFile", "No setup active for tracking Events", "yellow")


def sub_callback(name: str):
    printer.title(f"Launching attached App: {name}!")


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Status
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

type StatusSignature = Callable[
    [object, list[type[BaseException]], bool], None
]
type ExceptionFormater = Callable[type[BaseException], str]


class SetupStatus(PrintOption[StatusSignature]):
    """Show SafeTyper summary and optional all Exceptions with Handler"""

    def _load_default_function(self):
        return partial(
            self._template,
            box1=boxes.EDGE,
            color1="yellow",
            exc_formater=self._format_colorful,
        )

    def _template(
        self,
        safe_typer: object,
        exceptions: list[BaseException],
        show_all: bool,
        box1: Box | None,  # LATER: handle default box other than with None...
        color1: ColorName,
        exc_formater: ExceptionFormater,
    ):
        _safe_typer = c(safe_typer, color1)
        text_safe = f"{_safe_typer} Ready for Execution"
        printer.box(text_safe, frame=color1, box=box1)

        printer(f"Attached {len(exceptions)} Error Handler", _i=2)

        if show_all:
            for exception in exceptions:
                printer(exc_formater(exception), _i=4)

        printer("Some statistics: ...", _i=2)
        printer.line("yellow")

    def _set_more_if_desired(self):
        param_grid: dict[str, Any] = {
            "box1": [boxes.OPEN, boxes.EDGE, None],
            "exc_formater": [self._format_raw, self._format_colorful],
        }
        kwargs: dict[str, str] = {"color1": "yellow"}
        self.grid(self._template, param_grid, common_kwargs=kwargs)

    @staticmethod
    def _format_raw(exception: type[BaseException]) -> str:
        return str(exception)

    @staticmethod
    def _format_colorful(exception: type[BaseException]) -> str:
        # TODO: replace by colorize.module_path?
        project, *modules = exception.__module__.split(".")
        module: str = ".".join([c.c(project), *[c.g(m) for m in modules]])
        error = f"{c.red(exception.__name__)}"
        return f"{module}.{error}"


status = SetupStatus(select_mode=SelectMode.RANDOM)
