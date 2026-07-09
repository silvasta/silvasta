"""
Setup Loguru for Console, *.log or *.json

Load param from ConfigManager.setup_info.log or create fresh setup.

If all options are unused or fail, LogParam defaults are applied.

"""

import sys
from pathlib import Path

from loguru import logger

from ..path import PathGuard
from .format import load_format_pattern, ndjson_formatter
from .param import LogParam, LogSetupResult

# Cache Result to prevent multiple calls
_setup_result: LogSetupResult | None = None


def setup_logging(
    log_level_override: str | None = None,
    quiet: bool = False,
    log_file: Path | None = None,
    log_to_file: bool = True,
    param: LogParam | None = None,
) -> LogSetupResult:
    """
    Setup Loguru for Console or File output and return applied param.

    - log_file overrides log_to_file
    - otherwise and if needed, LogParam provides path components
    - LogSetupResult provides the finally applied paths and settings

    """  # TODO: something about json

    global _setup_result

    if _setup_result is not None:
        return _setup_result

    log_param: LogParam = param or LogParam()

    if log_level_override is not None:
        log_param.log_level = log_level_override

    logger.remove()

    if not quiet:  # Terminal output
        logger.add(
            sink=sys.stderr,
            level=log_param.log_level,
            format=load_format_pattern(),
            colorize=True,
        )

    if log_to_file or log_file:
        log_file_path: Path = _ensure_log_file(log_param, log_file)
        logger.add(
            sink=log_file_path,
            level="DEBUG",  # Always keep debug detail for files
            rotation=log_param.rotation,
            retention=log_param.retention,
            compression="zip",
            backtrace=True,  # Note: this can reveal sensitive data!
            diagnose=True,  # Shows variable values in logs!
            enqueue=True,  # Thread-safe
        )

        # TODO: make toggles inside param and include .json in result

        logger.add(
            sink=log_file_path.with_suffix(".jsonl"),
            format=ndjson_formatter,
            level="DEBUG",
            rotation=log_param.rotation,
            retention=log_param.retention,
            enqueue=True,  # Keeps JSON writing thread-safe
        )
    if not quiet and not log_to_file:
        print("Warning: Logging is completely disabled.")

    _setup_result = LogSetupResult.from_param(
        log_file=log_file_path,  # WARN: ensure log_file_path is set
        selected_param=log_param,
    )
    return _setup_result


@PathGuard.file(default_content="", raise_error=False)
def _ensure_log_file(log_param: LogParam, log_file: Path | None) -> Path:
    """Ensure at least empty log file exists"""
    return log_file or log_param.log_file


def setup_minimal_logging(level: str = "WARNING"):
    """Kill noise immediately for clean bootstrap but show critical issues"""
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        level=level,
        format="{time:HH:mm:ss} | <level>{level:8}</level> | {message}",
    )
