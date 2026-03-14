import sys
from pathlib import Path
from types import SimpleNamespace

from ..utils.path import find_project_root, pyproject_log_section

try:
    from loguru import logger
except ImportError:
    raise ImportError(
        "Loguru is required for this module. Install with: 'silvasta[log|cli|tui]'"
    )  # TODO: better message / handling of optinal dependency


_is_configured = False


def setup_logging(
    project_root: Path | None = None,
    log_level_override: str | None = None,
    log_to_file: bool = True,
    quiet: bool = False,
):
    """Configure Loguru based on pyproject.toml settings"""

    global _is_configured
    if _is_configured:
        return logger

    # TODO: parameter input
    # - figure out how it should work without toml
    # - per argument? env variable? new config file type?

    if project_root is None:
        # For now: let it crash without valid project_root and toml
        project_root: Path = find_project_root("pyproject.toml")

    try:  # Parse config from pyproject.toml file
        log_config: SimpleNamespace = pyproject_log_section()
        # Values
        log_level = log_config.level
        log_filename = log_config.file_name
        rotation = log_config.rotation
        retention = log_config.retention

    except AttributeError:
        log_level = "INFO"
        rotation = "5 MB"
        retention = "1 week"
        log_filename = "debug.log"

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
        log_dir: Path = project_root / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path: Path = log_dir / log_filename

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
