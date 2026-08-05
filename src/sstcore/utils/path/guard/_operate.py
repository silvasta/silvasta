"""
File System Operations

- Transfer
- Delete
"""

__all__: list[str] = [
    # transfer operations
    "rotate",
    "copy",
    "hardlink",
    "symlink",
    # delete operations
    "remove",
    "trash",
    "prune",
]

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from ....error import PathGuardError, PathGuardReason
from ....format.reflect import cls_name
from ....port.pathguard import SyncMode
from ...functor import Functor
from ._ensure import _ensure_dir_logic, _get_unique_candidate, find_sequence
from ._input import PathInput, PathSpec

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Transfer Operations
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@dataclass
class TransferStrategy(Functor[[Path, Path, SyncMode], Path]):
    """Provide Skeleton for specific Function binding"""

    # logger.info(f"{self}: {relative_string(source, target)}")


def check_sync_mode(target: Path, mode: SyncMode) -> Path:
    """Provide SyncMode Path that is valid to write or Raise"""
    if not target.exists():
        return _ensure_dir_logic(target.parent)
    match mode:
        case SyncMode.OVERRIDE:
            return target
        case SyncMode.INCREMENT:
            return _get_unique_candidate(path=target, ensure_parent=True)
        case SyncMode.IGNORE:
            raise PathGuardError(PathGuardReason.SYNC, target=target)


def _handle_hardlink(error: Exception, source: Path, target: Path):
    if isinstance(error, OSError):
        raise PathGuardError(
            PathGuardReason.HARDLINK,
            source=source,
            target=target,
            catched=error,
        ) from error
    else:
        raise error


def prepare(func: Callable[[Path, Path], Any]):
    def run(source: Path, target: Path, mode: SyncMode):
        transferable: Path = check_sync_mode(target, mode)
        transfered: Path = func(source, transferable)
        return transfered

    return run


Rotate: TransferStrategy[[Path, Path], Path] = TransferStrategy.from_func(
    func=prepare(lambda source, target: source.move(target)),
    name="PathGuard - Rotate",
)

Copy: TransferStrategy[[Path, Path], Path] = TransferStrategy.from_func(
    func=prepare(lambda source, target: source.copy(target)),
    name="PathGuard - Copy",
)

Symlink: TransferStrategy[[Path, Path], Path] = TransferStrategy.from_func(
    func=prepare(lambda source, target: target.symlink_to(source)),
    name="PathGuard - Simlink",
)

Hardlink: TransferStrategy[[Path, Path], Path] = TransferStrategy.from_func(
    func=prepare(lambda source, target: target.hardlink_to(source)),
    name="PathGuard - Hardlink",
    handle=_handle_hardlink,
)


def hardlink(
    source: PathInput,
    target: PathInput,
    mode: SyncMode = SyncMode.INCREMENT,
) -> Path:
    """Create Hardlink at Target Pointing to Source"""

    return Hardlink.safe(
        source=PathSpec.ok(target=source, must_exists=True),
        target=PathSpec.ok(target=target),
        mode=mode,
    )


def symlink(
    source: PathInput,
    target: PathInput,
    mode: SyncMode = SyncMode.INCREMENT,
) -> Path:
    """Create Absolute Symlink at Target Pointing to Source"""

    return Symlink.safe(
        source=PathSpec.ok(target=source, must_exists=True, resolve=True),
        target=PathSpec.ok(target=target),
        mode=mode,
    )


def copy(
    source: PathInput,
    target: PathInput,
    mode: SyncMode = SyncMode.INCREMENT,
) -> Path:
    """Copy Source to Target"""

    return Rotate.safe(
        source=PathSpec.ok(target=source, must_exists=True),
        target=PathSpec.ok(target=target),
        mode=mode,
    )


def rotate(
    source: PathInput,
    target: PathInput,
    mode: SyncMode = SyncMode.INCREMENT,
    reset: bool = False,
) -> Path:
    """Move Source to Target and if reset: Create empty File or Dir"""

    source_ok: Path = PathSpec.ok(target=source, must_exists=True)
    is_directory: bool = source_ok.is_dir()  # store for reset logic

    transfered: Path = Rotate.safe(
        source=(source_ok), target=PathSpec.ok(target=target), mode=mode
    )
    if reset:
        if is_directory:
            source_ok.mkdir()
        else:
            source_ok.touch()
    return transfered


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Delete Operations
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def _clear_file_or_folder(
    target: PathInput,
    clear_strategy: Callable[[Path], Any],
) -> bool:
    """Execute Delete Operation in Safe Environment"""

    # Extract Name of clear_strategy for log
    _clear: str = getattr(clear_strategy, "__name__", "_clear")
    clear: str = _clear.strip("_").capitalize()

    try:
        target_ok: Path = PathSpec.ok(target, must_exists=True)
        # IDEA: as soon as Functor handles more than 1 error...
        clear_strategy(target_ok)
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
