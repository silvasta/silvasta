import sys
from pathlib import Path

from loguru import logger

from ..path import PathGuard
from .param import LogParam, LogSetupResult

# from .sink import serialize_to_ndjson


def setup_minimal_logging(level: str = "WARNING"):
    """Kill noise immediately. Users see almost nothing during bootstrap."""
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        level=level,
        format="{time:HH:mm:ss} | <level>{level:8}</level> | {message}",
    )


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
    Setup Loguru for Console or File output and provide applied param.

    Load param from ConfigManager.setup_info.log or create fresh setup

    - log_file overrides log_to_file
    - otherwise and if needed, LogParam provides path components
    - LogSetupResult provides the finally applied paths and settings

    If all options are unused or fail, LogParam defaults are applied

    """
    global _setup_result

    if _setup_result is not None:
        return _setup_result

    log_param: LogParam = param or LogParam()

    if log_level_override is not None:
        log_param.log_level = log_level_override

    logger.remove()

    if not quiet:  # Terminal output
        format_parts: list[str] = [  # MOVE: to format
            "<green>{time:HH:mm:ss}</green>",
            "<level>{level: <8}</level>",
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>"
            " - <level>{message}</level>",
        ]
        logger.add(
            sys.stderr,
            level=log_param.log_level,
            format=" | ".join(format_parts),
            colorize=True,
        )
    # AI_TASK: discuss new sink to json without disabling the others

    # File output
    if log_to_file or log_file:
        log_file_path: Path = _ensure_log_file(log_param, log_file)
        logger.add(
            sink=log_file_path,
            level="DEBUG",  # Always keep debug detail for files
            # IDEA: 3 - format=lambda r: serialize_to_ndjson(r),
            rotation=log_param.rotation,
            retention=log_param.retention,
            compression="zip",
            backtrace=True,  # Note: this can reveal sensitive data!
            diagnose=True,  # Shows variable values in logs!
            enqueue=True,  # Thread-safe
        )

        # IMPORTANT: attach serialize_to_ndjson

        # IDEA: 4
        log_file_json: Path = log_file_path.with_suffix(".jsonl")
        logger.add(
            log_file_json,
            serialize=True,  # activate JSON
            level="DEBUG",
            rotation=log_param.rotation,
            enqueue=True,
        )
    if not quiet and not log_to_file:
        print("Warning: Logging is completely disabled.")

    _setup_result = LogSetupResult.from_param(
        log_file=log_file_path, selected_param=log_param
    )
    return _setup_result


@PathGuard.file(default_content="", raise_error=False)
def _ensure_log_file(log_param: LogParam, log_file: Path | None) -> Path:
    """Select log path and ensure there is a File"""
    return log_file or log_param.log_file
