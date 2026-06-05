from loguru import logger

from sstcore.utils.log import LogSetupResult

from ..config.manager import ConfigSetupParam
from ..utils import printer
from ..utils.print import ColorBox

c: ColorBox = printer.colorbox(mode="bold")

_config_file = c.blue("Config File")
_config_param = c.yellow("ConfigSetupParam")

_log_file = c.blue("Log File")
_log_param = c.yellow("LogParamSource")


def main_callback_config_setup(param: ConfigSetupParam | None):
    """Intro Sketch: engine._main_callback:config"""
    if not param:
        text = f"Typer Setup: {_config_file} not provided by {_config_param}"
        printer.warn(text)

    elif not (path := param.config_file).is_file():
        text = f"{_config_file} provided by {_config_param} not on disk!"
        printer.danger(text)
        printer(param)
        logger.error(f"Missing config file: {path=}")
    else:
        printer.title(path, title=_config_file)  # TEST:


def main_callback_log_setup(result: LogSetupResult):
    """Intro End: engine._main_callback:log"""
    if result.print_at_setup:
        printer(result)
    printer(f"  {_log_param} {result.setup_source}")
    if result.log_file:
        printer.title(result.log_file, title=_log_file)
    else:
        printer.warn(f"No {_log_file} active for tracking Events.")
