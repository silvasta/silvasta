import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Self

from loguru import logger
from pydantic import BaseModel

from ..utils.path import pyproject_log_section, recursive_root
from .pathguard import PathGuard


class LogParam(BaseModel):
    # setup behaviour
    print_at_setup: bool = False

    # dir and file
    log_dir: str = "logs"
    log_filename: str = "debug.log"

    # runtime behaviour and file management
    log_level: str = "INFO"
    retention: str = "1 week"
    rotation: str = "5 MB"


# Result cache to prevent multiple calls from re-run
_setup_result: LogSetupResult | None = None


def setup_logging(
    log_level_override: str | None = None,
    quiet: bool = False,
    log_file: Path | None = None,  # overrides 'log_to_file' if set
    log_to_file: bool = True,
    from_toml: bool = False,
    param: LogParam | None = None,
) -> LogSetupResult:
    """Setup Loguru for Console or File output and provide applied setup.
    log_file overrides log_to_file, otherwise path is composed if needed,
    load param from pyproject.toml or f.e. param=ConfigManager.setup_info.log
    if all options are unused or fail, defaults are applied.
    """

    global _setup_result
    if _setup_result is not None:
        return _setup_result

    # Select Param source

    if from_toml and (log_param := _load_from_toml()):
        log_config_source = "pyproject.toml"

    elif log_param := param:
        log_config_source = "param"

    else:
        log_config_source = "default"
        log_param = LogParam()

    if log_level_override is not None:
        log_param.log_level: str = log_level_override

    logger.remove()

    if not quiet:  # Terminal output
        format_parts: list[str] = [
            "<green>{time:HH:mm:ss}</green>",
            "<level>{level: <8}</level>",  # LATER: check size of level
            "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        ]
        logger.add(
            sys.stderr,
            level=log_param.log_level,
            format=" | ".join(format_parts),
            colorize=True,
        )

    if log_to_file or log_file:  # File output
        log_file_path: Path = _ensure_log_file_path(log_param, log_file)
        logger.add(
            log_file_path,
            level="DEBUG",  # Always keep debug detail for files
            rotation=log_param.rotation,
            retention=log_param.retention,
            compression="zip",
            backtrace=True,  # Note: this can reveal sensitive data!
            diagnose=True,  # Shows variable values in logs!
            enqueue=True,  # Thread-safe
        )

    if not quiet and not log_to_file:
        print("Warning: Logging is completely disabled.")

    _setup_result = LogSetupResult.from_param(
        setup_source=log_config_source,
        log_file=log_file_path,
        selected_param=log_param,
    )

    return _setup_result


class LogSetupResult(BaseModel):
    setup_source: str
    log_file: Path | None

    # from LogParam
    log_level: str = "INFO"
    retention: str = "1 week"
    rotation: str = "5 MB"

    @classmethod
    def from_param(
        cls,
        setup_source: str,
        log_file: Path | None,
        selected_param: LogParam,
    ) -> Self:
        return cls(
            setup_source=setup_source,
            log_file=log_file,
            log_level=selected_param.log_level,
            retention=selected_param.retention,
            rotation=selected_param.rotation,
        )


@PathGuard.file(default_content="", raise_error=False)
def _ensure_log_file_path(
    log_param: LogParam,
    log_file: Path | None,
) -> Path:
    """Use provided Path or compose from LogParam"""

    if log_file is not None:
        return log_file

    project_root: Path = (
        recursive_root(path=Path.cwd(), indicator="pyproject.toml")
        or Path.cwd()
    )
    return project_root / log_param.log_dir / log_param.log_filename


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
        logger.error("Failed to extract LogParams from pyproject.toml")
        return None
