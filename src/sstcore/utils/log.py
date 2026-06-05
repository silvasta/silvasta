import sys
from pathlib import Path
from typing import Self

from loguru import logger
from pydantic import BaseModel, Field

from .path import PathGuard
from .path.search import any_root


class LogParam(BaseModel):
    # setup behaviour
    print_at_setup: bool = True
    setup_source: str = "Defaults: utils.log.LogParam"

    # dir and file
    log_dir: Path = Field(default_factory=any_root)
    log_filename: str = "debug.log"

    # runtime behaviour and file management
    log_level: str = "INFO"
    retention: str = "1 week"
    rotation: str = "5 MB"

    @property
    def log_file(self) -> Path:
        return self.log_dir / self.log_filename

    def with_source(self, source: str) -> Self:
        self.setup_source: str = source
        return self

    def attach_logname(self, name: str) -> Self:
        if stem := name.rstrip(".log").strip():
            self.log_filename = f"{stem}.log"
        return self


# Result cache to prevent multiple calls from re-run
_setup_result: LogSetupResult | None = None


def setup_logging(
    log_level_override: str | None = None,
    quiet: bool = False,
    log_file: Path | None = None,  # overrides 'log_to_file' if set
    log_to_file: bool = True,
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

    log_param: LogParam = param or LogParam()

    if log_level_override is not None:
        log_param.log_level = log_level_override

    logger.remove()

    # Terminal output
    if not quiet:
        format_parts: list[str] = [  # LATER: check format, size of level, etc
            "<green>{time:HH:mm:ss}</green>",
            "<level>{level: <8}</level>",
            "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        ]
        logger.add(
            sys.stderr,
            level=log_param.log_level,
            format=" | ".join(format_parts),
            colorize=True,
        )

    # File output
    if log_to_file or log_file:
        logger.add(
            log_file_path := _ensure_log_file(log_param, log_file),
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
        log_file=log_file_path, selected_param=log_param
    )

    return _setup_result


class LogSetupResult(BaseModel):
    print_at_setup: bool
    setup_source: str

    # Final Path that was taken (usually the composed from LogParam)
    log_file: Path | None

    # from LogParam
    log_level: str
    retention: str
    rotation: str

    @classmethod
    def from_param(
        cls, log_file: Path | None, selected_param: LogParam
    ) -> Self:
        return cls(
            print_at_setup=selected_param.print_at_setup,
            setup_source=selected_param.setup_source,
            log_file=log_file,
            log_level=selected_param.log_level,
            retention=selected_param.retention,
            rotation=selected_param.rotation,
        )


@PathGuard.file(default_content="", raise_error=False)
def _ensure_log_file(log_param: LogParam, log_file: Path | None) -> Path:
    return log_file or log_param.log_file
