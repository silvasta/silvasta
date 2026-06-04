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


def find_project_root(
    start: Path | None = None,
    indicator: str = "pyproject.toml",
    strict=False,
) -> Path | None:
    """Call Recursive Root search function with Project arguments"""
    start: Path = start or Path.cwd()

    if project_root := recursive_root(path=start, indicator=indicator):
        logger.debug(f"found {project_root=}")
        return project_root

    msg = f"recursive_root failed for: {indicator=}, {start=}"
    if strict:
        logger.error(msg)  # LATER: ProjectRootMissingError? with indicator,
        raise FileNotFoundError("No Project Root found!")
    else:
        logger.info(msg)
        return None


def get_project_root(
    start: Path | None = None,
    indicator: str = "pyproject.toml",
) -> Path:
    """Get project root or FileNotFoundError."""
    if not (project_root := find_project_root(start, indicator, strict=True)):
        logger.error("utils.path.search: (find_)project_root pipeline broken!")
        raise FileNotFoundError("No Project Root found!")

    return project_root
