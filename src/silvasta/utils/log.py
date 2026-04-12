import sys
from pathlib import Path
from types import SimpleNamespace

from loguru import logger
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel

from ..utils.path import (
    pyproject_log_section,
    recursive_root,
)

_is_configured = False


class LogParam(BaseModel):
    log_dir: str
    log_filename: str
    log_level: str
    retention: str
    rotation: str


def setup_logging(
    log_level_override: str | None = None,
    quiet: bool = False,
    log_file: Path | None = None,
    log_to_file: bool = True,
    param: dict[str, str | LogParam] | None = None,
    show_log_param: bool = False,
):
    """Setup Loguru with pyproject.toml, param=config.compose_setup_param()
    log_file path overrides project_root concat path and sets log_to_file=True,
    if all options are unused or fail, defaults are applied.
    """

    global _is_configured
    if _is_configured:
        return logger

    param: dict[str, str | LogParam] = param or {}

    log_param: LogParam = _select_log_param(param)

    if log_level_override is not None:
        log_param.log_level: str = log_level_override

    logger.remove()

    if not quiet:
        format_parts: list[str] = [
            "<green>{time:HH:mm:ss}</green>",
            "<level>{level: <8}</level>",  # LATER: check size of level
            "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        ]
        format: str = " | ".join(format_parts)
        logger.add(
            sys.stderr,
            level=log_param.log_level,
            format=format,
            colorize=True,
        )

    if log_file_path := _check_log_file_args(log_file, log_to_file, log_param):
        param["log_file"] = str(log_file_path)

        if show_log_param:
            Console().print(param)

        to_print: list = [
            param.get("config_file", "config file lost..."),
            param.get("log_file", "log file lost..."),
        ]
        title: str = param.get("log_param", "Log to File")  # ty:ignore

        Console(style="yellow").print(
            Panel("\n".join(to_print), title=title, title_align="right")
        )

        logger.add(
            log_file_path,
            level="DEBUG",  # Always keep debug detail in files
            rotation=log_param.rotation,
            retention=log_param.retention,
            compression="zip",
            backtrace=True,  # Note: this can reveal sensitive data!
            diagnose=True,  # Shows variable values in logs!
            enqueue=True,  # Thread-safe
        )

    if not quiet and not log_to_file:
        print("Warning: Logging is completely disabled.")

    _is_configured = True

    return logger


def _check_log_file_args(
    log_file: Path | None,
    log_to_file: bool,
    log_param: LogParam,
) -> Path | None:
    """Use direct file path if avaliable, otherwise create composed path"""

    if log_file:
        log_file_path: Path = log_file

    elif log_to_file:
        project_root: Path = (
            recursive_root(path=Path.cwd(), indicator="pyproject.toml")
            or Path.cwd()
        )
        log_file_path: Path = (
            project_root / log_param.log_dir / log_param.log_filename
        )
    else:
        return None

    if not log_file_path.exists():
        # NOTE: maybe raise Error when log_file_path.parent not exists?
        print(f"Log file not found! Create empty file at: {log_file_path=}")
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        log_file_path.touch()

    return log_file_path


def _select_log_param(param: dict) -> LogParam:
    """Try extract pyproject.toml, then config, then use defaults"""

    if toml_log_param := _load_from_toml():
        log_param_text = "toml_log_param"
        log_param: LogParam = toml_log_param

    elif param:
        log_param_text = "config_log_param"
        log_param: LogParam = param.pop("log")

    else:
        log_param_text = "default_log_param"
        log_param = LogParam(
            log_dir="logs",
            log_filename="debug.log",
            log_level="INFO",
            retention="1 week",
            rotation="5 MB",
        )

    param["log_param"] = f"Using {log_param_text}"

    return log_param


def _load_from_toml():
    """Find pyproject.toml, extract log section and params, or get None"""

    try:  # parse config from pyproject.toml file
        log_config: SimpleNamespace = pyproject_log_section()
        toml_param = LogParam(
            log_dir=log_config.log_dir,
            log_filename=log_config.file_name,
            log_level=log_config.level,
            retention=log_config.retention,
            rotation=log_config.rotation,
        )
        logger.debug("LogParams extracted from pyproject.toml")
        return toml_param

    except AttributeError:
        logger.debug("Failed to extract LogParams from pyproject.toml")
        return None
