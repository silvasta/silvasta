"""
Launch Log setup configured with LogParam

Three different setups: (any combination is possible)
  - print to console
  - write to logfile.log
  - write to logfile.jsonl

- Cache and return the applied setup param and block another setup
- Provied function to fetch or reset the cached result (*unlock*)

- Minimal Logging: intended to kill bootstrap noise without complete shutdown

                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "setup_logging",
    "reset_log_result",
    "fetch_log_result",
    "setup_minimal_logging",
]

import sys

from loguru import logger

from ...port.config import Log  # FIX: remove or build!
from ._format import load_format_pattern, ndjson_formatter
from ._param import LogParam


def setup_logging(param: Log | None = None) -> LogParam:
    """Setup Loguru for Console and Files (*.log and *.jsonl)"""

    global _setup_param

    if _setup_param is not None:
        return _setup_param

    param: Log = param or LogParam()

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


_setup_param: LogParam | None = None


def reset_log_result() -> None:
    """Allow setup_logging to run again"""
    global _setup_param
    _setup_param = None


def fetch_log_result() -> LogParam | None:
    """Fetch result of setup_logging"""
    global _setup_param
    return _setup_param


def setup_minimal_logging(level: str = "WARNING"):
    """Kill noise immediately for clean bootstrap but show critical issues"""
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        level=level,
        format="{time:HH:mm:ss} | <level>{level:8}</level> | {message}",
    )
