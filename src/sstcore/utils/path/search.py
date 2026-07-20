# TODO: explain

from pathlib import Path

from loguru import logger


def recursive_root(path: Path, indicator: str) -> Path | None:
    """Find Root by Indicator while iterating parent paths upwards"""

    if (path / indicator).exists():
        return path
    elif path == path.parent:
        return None
    else:
        return recursive_root(path.parent, indicator)


def recursive_parent(path: Path, parent_dir_name: str) -> Path | None:
    """Find closest Parent Directory matching a specific Name"""

    if path.name == parent_dir_name:
        return path
    elif path == path.parent:
        return None
    else:
        return recursive_parent(path.parent, parent_dir_name)


def any_root() -> Path:
    return find_project_root() or Path.cwd()


def find_project_root(
    start: Path | None = None,
    indicator: str = "pyproject.toml",
) -> Path | None:
    """Search Project Root"""
    start: Path = start or Path.cwd()

    if project_root := recursive_root(path=start, indicator=indicator):
        logger.debug(f"found {project_root=}")
        return project_root
    else:
        logger.info(f"No Project Root found: {indicator=}, {start=}")
        return None


def get_project_root(
    start: Path | None = None,
    indicator: str = "pyproject.toml",
) -> Path:
    """Project Root or Raise"""

    if project_root := find_project_root(start, indicator):
        return project_root

    # TASK: together with PathGuardError, including indicator
    raise FileNotFoundError(f"No Project Root found: {indicator=}, {start=}")
