from collections.abc import Callable
from enum import StrEnum, auto
from pathlib import Path
from typing import Any

from loguru import logger

from ._config import PathConfig, PathInput, _state
from ._ensure import (
    _ensure_dir_logic,
    _ensure_input,
    _get_unique_candidate,
    find_sequence,
)
from ._helper import relative_string


class SyncMode(StrEnum):
    INCREMENT = auto()
    OVERRIDE = auto()
    IGNORE = auto()

    def check_conflict(self, target: Path) -> Path:
        if not target.exists():
            _ensure_dir_logic(target.parent)
            return target

        match self:
            case SyncMode.OVERRIDE:
                logger.warning(f"Overriding existing File at {target=}")
                return target
            case SyncMode.INCREMENT:
                return _get_unique_candidate(path=target, ensure_parent=True)
            case SyncMode.IGNORE:
                raise FileExistsError("Catch error for SyncMode.IGNORE")


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Transfer Operations
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def rotate(
    source: PathInput,
    target: PathInput,
    sync_mode: str | SyncMode = "increment",
    reset: bool = False,
) -> Path:
    """Moves source (file or dir) to target, handles unique naming collisions,
    if reset=True, recreates empty file or directory at original 'source' location"""

    # TASK: similar pipeline as in _clear_file_or_folder

    _source: Path = _ensure_input(
        PathConfig.from_path_input(source, must_exists=True)
    )
    _target: Path = _ensure_input(target)
    sync_mode = SyncMode(sync_mode)

    # Store type for reset logic later
    is_directory: bool = _source.is_dir()

    _source.move(inspected_target := sync_mode.check_conflict(_target))
    relative: str = relative_string(_source, inspected_target)
    logger.info(f"Rotated: {relative}")

    if reset:
        if is_directory:
            _source.mkdir()
            logger.debug(f"Recreated empty directory: {source}")
        else:
            _source.touch()
            logger.debug(f"Reset empty file: {source}")

    return inspected_target


def copy(
    source: PathInput,
    target: PathInput,
    sync_mode: str | SyncMode = "increment",
) -> Path:
    """Copy source (file or dir) to target, handles unique naming collisions"""

    # TASK: similar pipeline as in _clear_file_or_folder

    _source: Path = _ensure_input(
        PathConfig.from_path_input(source, must_exists=True)
    )
    _target: Path = _ensure_input(target)
    sync_mode = SyncMode(sync_mode)

    _source.copy(inspected_target := sync_mode.check_conflict(_target))
    relative: str = relative_string(_source, inspected_target)

    if _state.debug:
        logger.debug(f"Copied: {relative}")

    return inspected_target


def hardlink(
    source: PathInput,
    target: PathInput,
    sync_mode: str | SyncMode = "override",
) -> Path:
    """Create a hardlink of source to target, handles unique naming collisions"""

    # TASK: similar pipeline as in _clear_file_or_folder

    _source: Path = _ensure_input(
        PathConfig.from_path_input(source, must_exists=True)
    )
    _target: Path = _ensure_input(target)
    sync_mode = SyncMode(sync_mode)

    inspected_target: Path = sync_mode.check_conflict(_target)

    try:
        inspected_target.hardlink_to(_source)
    except OSError as e:
        logger.error("Hardlink failed! Source and Target on same drive?")
        logger.error(f"{source=}, {target=}")
        raise e

    relative: str = relative_string(_source, inspected_target)

    if _state.debug:
        logger.debug(f"Hardlinked: {relative}")

    return inspected_target


def symlink(
    source: PathInput,
    target: PathInput,
    sync_mode: str | SyncMode = "increment",
) -> Path:
    """Create absolute symlink of source to target, handles unique naming collisions"""

    # TASK: similar pipeline as in _clear_file_or_folder

    _source: Path = _ensure_input(
        PathConfig.from_path_input(source, must_exists=True, resolve=True)
    )
    _target: Path = _ensure_input(target)
    sync_mode = SyncMode(sync_mode)

    inspected_target: Path = sync_mode.check_conflict(_target)
    inspected_target.symlink_to(_source)

    relative: str = relative_string(_source, inspected_target)

    if _state.debug:
        logger.debug(f"Symlinked: {relative}")

    return inspected_target


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Delete Operations
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def _clear_file_or_folder(
    target: PathInput, clear_strategy: Callable[[Path], Any]
) -> bool:
    """Handle args, logs and errors for deleting files or folders"""
    _clear: str = getattr(clear_strategy, "__name__", "_clear")
    clear: str = _clear.strip("_").capitalize()
    try:
        _target: Path = _ensure_input(
            PathConfig.from_path_input(target, must_exists=True)
        )
        clear_strategy(_target)
        logger.success(f"{clear}: {target}")
        return True

    except FileNotFoundError:
        logger.error(f"Nothing to {clear}: missing {target=}")
    except OSError as e:
        logger.error(f"OSError for {clear}: {target=}\n{e}")
    return False


def remove(target: Path | str) -> bool:
    """Remove file or folder at target location"""

    def _remove(path: Path):
        if path.is_dir():
            import shutil  # LATER: upgrade with pathlib?

            shutil.rmtree(path)
        else:
            path.unlink()

    return _clear_file_or_folder(target, clear_strategy=_remove)


def trash(target: PathInput) -> bool:
    """Move file or folder at target location to system trash"""

    def _trash(path: Path):
        from send2trash import send2trash

        send2trash(path)

    return _clear_file_or_folder(target, clear_strategy=_trash)


def prune(
    base_target: PathInput, remaining: int = 5, trash=False
) -> list[Path]:
    """Remove oldest files/dirs from sequence (name_NUM{.*}) until remaining"""

    if remaining >= len(sequence := find_sequence(base_target)):
        return []

    paths_to_delete: list[Path] = sequence[remaining:]

    _prune: Callable[[Path], bool] = trash if trash else remove

    return [path for path in paths_to_delete if _prune(path)]
