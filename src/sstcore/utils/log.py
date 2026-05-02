import sys
from pathlib import Path
from types import SimpleNamespace

from loguru import logger
from pydantic import BaseModel

from ..utils.path import (
    pyproject_log_section,
    recursive_root,
)


class LogParam(BaseModel):
    log_dir: str = "logs"
    log_filename: str = "debug.log"
    log_level: str = "INFO"
    retention: str = "1 week"
    rotation: str = "5 MB"
    print_log_param: bool = False


class LogSetupResult(BaseModel):
    config_source: str
    log_file: Path | None
    selected_param: LogParam


# Result cache to prevent multiple calls from re-run
_setup_result: "LogSetupResult | None" = None


def setup_logging(
    log_level_override: str | None = None,
    quiet: bool = False,
    log_file: Path | None = None,
    log_to_file: bool = True,
    param: LogParam | None = None,
) -> LogSetupResult:
    """Setup Loguru with pyproject.toml, param=config.compose_setup_param().log
    log_file path overrides project_root concat path and sets log_to_file=True,
    if all options are unused or fail, defaults are applied.
    """

    global _setup_result
    if _setup_result is not None:
        return _setup_result

    # Priority 1
    if log_param := _load_from_toml():
        log_config_source = "toml_log_param"

    # Priority 2
    elif log_param := param:
        log_config_source = "config_log_param"

    else:  # fallback
        log_config_source = "default_log_param"
        log_param = LogParam()

    if log_level_override is not None:
        log_param.log_level: str = log_level_override

    logger.remove()

    if not quiet:
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

    if log_file_path := _check_log_file_args(log_file, log_to_file, log_param):
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

    _setup_result = LogSetupResult(
        config_source=log_config_source,
        log_file=log_file_path,
        selected_param=log_param,
    )

    return _setup_result


def _check_log_file_args(
    log_file: Path | None,
    log_to_file: bool,
    log_param: LogParam,
) -> Path | None:
    """Use direct file path if available, otherwise create composed path"""

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
