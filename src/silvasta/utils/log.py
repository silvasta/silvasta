import sys
from pathlib import Path
from types import SimpleNamespace

from ..utils.path import find_project_root, pyproject_log_section
from .pathguard import PathGuard

try:
    from loguru import logger

    _loguru_loaded = True
except ImportError:
    # TASK: this but for entire silvasta.utils
    # Delay crash for case:
    # - this file gets loaded but logger not needed
    _loguru_loaded = False


_is_configured = False


def setup_logging(
    project_root: Path | None = None,
    log_level_override: str | None = None,
    log_to_file: bool = True,
    quiet: bool = False,
):
    """Configure Loguru based on pyproject.toml settings"""

    if not _loguru_loaded:
        raise ImportError(
            "Loguru is required for this module. Install with: 'silvasta[log|cli|tui]'"
        )

    global _is_configured
    if _is_configured:
        return logger

    # TODO: parameter input
    # - figure out how it should work without toml
    # - per argument? env variable? new config file type?
    # -> combine with config/pydantic_settings

    if project_root is None:
        # For now: let it crash without valid project_root and toml
        project_root: Path = find_project_root("pyproject.toml")

    try:  # Parse config from pyproject.toml file
        log_config: SimpleNamespace = pyproject_log_section()
        # Values
        log_dir: str = log_config.log_dir
        log_filename: str = log_config.file_name
        log_level: str = log_config.level
        retention: str = log_config.retention
        rotation: str = log_config.rotation

    except AttributeError:
        # TODO: 1 fail, all fail now... separate somehow?
        log_dir = "logs"
        log_filename = "debug.log"
        log_level = "INFO"
        retention = "1 week"
        rotation = "5 MB"

    if log_level_override is not None:
        log_level: str = log_level_override

    logger.remove()

    if not quiet:
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            colorize=True,
        )

    if log_to_file:
        log_path = PathGuard.file(
            project_root / log_dir / log_filename,
            raise_error=False,
            default_content="",  # create empty file
        )
        print(log_path)
        logger.add(
            log_path,
            level="DEBUG",  # Always keep debug detail in files
            rotation=rotation,
            retention=retention,
            compression="zip",
            backtrace=True,  # Note: this can reveal sensitive data!
            diagnose=True,  # Shows variable values in logs!
            enqueue=True,  # Thread-safe
        )

    if not quiet and not log_to_file:
        print("Warning: Logging is completely disabled.")

    _is_configured = True
    return logger
