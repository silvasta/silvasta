from sstcore.utils.log import LogSetupResult

from ..utils import printer
from ..utils.paint import ColorBox

c: ColorBox = printer.colorbox(mode="bold")

_config_file = c.blue("Config File")

_log_file = c.blue("Log File")
_log_param = c.yellow("LogParamSource")


def main_callback_config_setup(config, from_default: bool):
    """Provide Information about Config setup"""

    if from_default:  # TASK: colorize
        text = f"Typer Setup: {config} loaded with Default Parameter"
        printer.warn(text)
    else:
        text = f"Typer Setup: {config} loaded with provided ConfigLoader"
        printer.warn(text)

    printer.title(config.setting_file, title=_config_file)


def main_callback_log_setup(result: LogSetupResult):
    """Provide Information about Log setup"""

    if result.print_at_setup:
        printer(result)

    if result.log_file:
        printer.title(result.log_file, title=_log_file)
    else:
        printer.warn(f"No {_log_file} active for tracking Events")
