"""
File System Operations

- Transfer
- Delete
"""

__all__: list[str] = [  # TODO:
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
from pathlib import Path

from loguru import logger

from ....brick.format import cls_name
from ....brick.func import SafeFunctor
from ....error import PathGuardError, PathGuardReason
from ....port.call import ErrorPolicy
from ....port.files import SyncMode
from ._ensure import _ensure_dir_logic, _get_unique_candidate, find_sequence
from ._input import PathInput, PathSpec


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


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Transfer Operations
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class TransferStrategy(SafeFunctor[[Path, Path], Path]):
    def __init__(self, **kwargs):
        kwargs.setdefault("error_policy", ErrorPolicy.RE_RAISE)
        super().__init__(**kwargs)

    check_sync_mode: Callable = staticmethod(check_sync_mode)

    def synced(self, source: Path, target: Path, mode: SyncMode) -> Path:
        """Apply SyncMode and Transfer Source to confirmed Target"""
        return self(source, check_sync_mode(target, mode))


def _rotate(source: Path, target: Path) -> Path:
    return source.rename(target)


Rotate: TransferStrategy = TransferStrategy(
    name="PathGuard - Rotate", func=_rotate
)

x = Rotate.name
y = Rotate()


def _copy(source: Path, target: Path) -> Path:
    return source.copy(target)


Copy = TransferStrategy(name="PathGuard - Copy", func=_copy)


def _symlink(source: Path, target: Path) -> Path:
    target.symlink_to(source)
    return target


Symlink = TransferStrategy(name="PathGuard - Simlink", func=_symlink)


def _hardlink(source: Path, target: Path) -> Path:
    target.hardlink_to(source)
    return target


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


Hardlink = TransferStrategy(
    name="PathGuard - Hardlink",
    func=_hardlink,
    catch=_handle_hardlink,
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

    transfered: Path = Rotate.synced(
        source=(source_ok), target=PathSpec.ok(target=target), mode=mode
    )
    if reset:
        if is_directory:
            source_ok.mkdir()
        else:
            source_ok.touch()
    return transfered


def copy(
    source: PathInput, target: PathInput, mode: SyncMode = SyncMode.INCREMENT
) -> Path:
    """Copy Source to Target"""

    return Rotate.synced(
        source=PathSpec.ok(target=source, must_exists=True),
        target=PathSpec.ok(target=target),
        mode=mode,
    )


def symlink(
    source: PathInput, target: PathInput, mode: SyncMode = SyncMode.INCREMENT
) -> Path:
    """Create Absolute Symlink at Target Pointing to Source"""

    return Symlink.synced(
        source=PathSpec.ok(target=source, must_exists=True, resolve=True),
        target=PathSpec.ok(target=target),
        mode=mode,
    )


def hardlink(
    source: PathInput, target: PathInput, mode: SyncMode = SyncMode.INCREMENT
) -> Path:
    """Create Hardlink at Target Pointing to Source"""

    return Hardlink.synced(
        source=PathSpec.ok(target=source, must_exists=True),
        target=PathSpec.ok(target=target),
        mode=mode,
    )


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Delete Operations
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class DeleteStrategy(SafeFunctor[[Path], bool]):
    """Execute Delete Operation in Safe Environment"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def clear(self, target: PathInput) -> bool:  # LATER: pass parsed PathInput
        try:
            target_ok: Path = PathSpec.ok(target, must_exists=True)
        except PathGuardError as error:
            self.emit(f"Failed to parse input: {error}", error=error)
        return self.safe(target_ok) is not None  # TEST:

    def on_error(self, error: Exception, target: PathInput) -> bool:
        logger.warning(f"{self.name}: {cls_name(error)}", error, target)
        return False


def _remove(path: Path) -> None:
    if path.is_dir():
        import shutil  # LATER: upgrade with pathlib?

        shutil.rmtree(path)
    else:
        path.unlink()


def _trash(path: Path):
    from send2trash import send2trash

    send2trash(path)


Remove = DeleteStrategy(
    name="PathGuard - Remove",
    func=_remove,
)
Trash = DeleteStrategy(
    name="PathGuard - Trash",
    func=_trash,
)
d = Remove.name


def remove(target: PathInput) -> bool:
    """Remove file or folder at target location"""
    return Remove(target)


def trash(target: PathInput) -> bool:
    """Move file or folder at target location to system trash"""
    return Trash(target)


def prune(
    base_target: PathInput, remaining: int = 5, *, use_trash: bool = False
) -> list[Path]:
    """Prune Sequence back to specified number of Remaining Targets"""
    if len(sequence := find_sequence(base_target)) <= remaining:
        return []
    paths_to_delete: list[Path] = sequence[remaining:]
    _prune: Callable[[Path], bool] = trash if use_trash else remove
    return [path for path in paths_to_delete if _prune(path)]
