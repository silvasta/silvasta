from collections.abc import Callable
from enum import StrEnum, auto
from pathlib import Path
from typing import Any

from loguru import logger

from sstcore.format.string import cls_name

from ....exceptions import PathGuardError, PathGuardReason
from ._ensure import _ensure_dir_logic, _get_unique_candidate, find_sequence
from ._helper import relative_string
from ._input import PathInput, PathSpec


class SyncMode(StrEnum):
    """Govern the Conflict Resolution Strategy for File Transfers"""

    INCREMENT = auto()
    OVERRIDE = auto()
    IGNORE = auto()

    def check_conflict(self, target: Path) -> Path:
        """Provide SyncMode Path that is valid to write or Raise"""

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
                raise PathGuardError(PathGuardReason.SYNC, target=target)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Transfer Operations
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def rotate(
    source: PathInput,
    target: PathInput,
    sync_mode: str | SyncMode = SyncMode.INCREMENT,
    reset: bool = False,
) -> Path:
    """Move Source to Target and if reset: Create empty File or Dir"""

    # LATER: similar pipeline as in _clear_file_or_folder

    _source: Path = PathSpec.ok(target=source, must_exists=True)
    _target: Path = PathSpec.ok(target=target)
    sync_mode = SyncMode(sync_mode)  # LATER: catch failed sync_mode:str?

    is_directory: bool = _source.is_dir()  # store for reset logic

    inspected_target: Path = sync_mode.check_conflict(_target)
    _source.move(inspected_target)
    relative: str = relative_string(_source, inspected_target)
    logger.info(f"Rotated: {relative}")  # MOVE: inside new strategy (later)

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
    sync_mode: str | SyncMode = SyncMode.INCREMENT,
) -> Path:
    """Copy Source to Target"""

    # LATER: similar pipeline as in _clear_file_or_folder

    _source: Path = PathSpec.ok(target=source, must_exists=True)
    _target: Path = PathSpec.ok(target=target)
    sync_mode = SyncMode(sync_mode)

    _source.copy(inspected_target := sync_mode.check_conflict(_target))

    return inspected_target


def hardlink(
    source: PathInput,
    target: PathInput,
    sync_mode: str | SyncMode = SyncMode.OVERRIDE,
) -> Path:
    """Create Hardlink at Target Pointing to Source"""

    # LATER: similar pipeline as in _clear_file_or_folder

    _source: Path = PathSpec.ok(target=source, must_exists=True)
    _target: Path = PathSpec.ok(target=target)
    sync_mode = SyncMode(sync_mode)

    inspected_target: Path = sync_mode.check_conflict(_target)

    try:
        inspected_target.hardlink_to(_source)
    except OSError as error:
        raise PathGuardError(
            PathGuardReason.HARDLINK,
            source=source,
            target=target,
            catched=error,
        ) from error

    return inspected_target


def symlink(
    source: PathInput,
    target: PathInput,
    sync_mode: str | SyncMode = SyncMode.INCREMENT,
) -> Path:
    """Create Absolute Symlink at Target Pointing to Source"""

    # LATER: similar pipeline as in _clear_file_or_folder

    _source: Path = PathSpec.ok(target=source, must_exists=True, resolve=True)
    _target: Path = PathSpec.ok(target=target)
    sync_mode = SyncMode(sync_mode)

    inspected_target: Path = sync_mode.check_conflict(_target)
    inspected_target.symlink_to(_source)

    return inspected_target


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Delete Operations
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def _clear_file_or_folder(
    target: PathInput,
    clear_strategy: Callable[[Path], Any],  # LATER: NamedFunctor
) -> bool:
    """Execute Delete Operation in Safe Environment"""

    # Extract Name of clear_strategy for log
    _clear: str = getattr(clear_strategy, "__name__", "_clear")
    clear: str = _clear.strip("_").capitalize()

    try:
        _target: Path = PathSpec.ok(target, must_exists=True)
        clear_strategy(_target)
        return True

    except (PathGuardError, OSError) as error:
        logger.warning(f"{cls_name(error)} for {clear}: {error} {target}")

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
    base_target: PathInput,
    remaining: int = 5,
    *,
    use_trash: bool = False,
) -> list[Path]:
    """Prune Sequence back to specified number of Remaining Targets"""

    if remaining >= len(sequence := find_sequence(base_target)):
        return []

    paths_to_delete: list[Path] = sequence[remaining:]

    _prune: Callable[[Path], bool] = trash if use_trash else remove

    return [path for path in paths_to_delete if _prune(path)]
