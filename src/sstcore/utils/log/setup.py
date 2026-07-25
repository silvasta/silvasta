"""Prepare selected logger, avoid multiple setups, provide minimal logger"""

__all__: list[str] = [
    "setup_logging",
    "setup_minimal_logging",
    "fetch_log_result",
    "reset_logging",
]

import sys

from loguru import logger

from .format import load_format_pattern, ndjson_formatter
from .param import LogParam

_setup_param: LogParam | None = None


def setup_logging(param: LogParam | None = None) -> LogParam:
    """Setup Loguru for Console and Files (*.log and *.jsonl)"""

    global _setup_param

    if _setup_param is not None:
        return _setup_param

    param: LogParam = param or LogParam()

    logger.remove()

    if param.log_to_console:
        logger.add(
            sink=sys.stderr,
            level=param.log_level,
            format=load_format_pattern(),
            colorize=True,
        )

    if param.log_to_file:
        logger.add(
            sink=param.log_file,
            level="DEBUG",  # Always keep debug detail for files
            rotation=param.rotation,
            retention=param.retention,
            compression="zip",
            backtrace=True,  # Note: this can reveal sensitive data!
            diagnose=True,  # Shows variable values in logs!
            enqueue=True,  # Thread-safe
        )

    if param.log_to_json:
        logger.add(
            sink=param.struct_log_file,
            format=ndjson_formatter,
            level="DEBUG",
            rotation=param.rotation,
            retention=param.retention,
            enqueue=True,  # Keeps JSON writing thread-safe
        )

    if not any([param.log_to_console, param.log_to_file, param.log_to_json]):
        print("Warning: Logging is completely disabled.")

    _setup_param = param

    return _setup_param


def setup_minimal_logging(level: str = "WARNING"):
    """Kill noise immediately for clean bootstrap but show critical issues"""
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        level=level,
        format="{time:HH:mm:ss} | <level>{level:8}</level> | {message}",
    )


def fetch_log_result() -> LogParam | None:
    """Fetch result of setup_logging"""
    global _setup_param
    return _setup_param


def reset_logging() -> None:
    """Allow setup_logging to run again"""
    global _setup_param
    _setup_param = None
