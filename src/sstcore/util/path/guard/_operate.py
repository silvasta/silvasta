"""
File System Operations

- Transfer: from source to target
- Delete: from target to ...

                         DependencyLevel.sstcore.util.path.guard[3]
"""

# IMPORTANT: Ensure PathArg is annotated for any Path in .__init__.pyi

__all__: list[str] = [  # LATER: what about Rotate,Trash,.. functor instances?
    "TransferStrategy",
    "check_sync_mode",
    "DeleteStrategy",
    # transfer
    "rotate",
    "copy",
    "hardlink",
    "symlink",
    # delete
    "remove",
    "trash",
    "prune",
]

from collections.abc import Callable
from pathlib import Path

from loguru import logger

from ....brick.field import PolicyField
from ....brick.reflect import clsname
from ....error import PathGuardError, PathGuardReason
from ....forge.func import SafeFunctor
from ....port.files import SyncMode
from ....port.functorial import ErrorPolicy
from . import _ensure, _increment
from ._arg import PathArg, ResolvedSource, SourcePath, TargetPath, castpath


def check_sync_mode(target: TargetPath, mode: SyncMode) -> Path:
    """Provide SyncMode Path that is valid to write or Raise"""

    if not target.exists():
        return _ensure._dir_logic(target.parent)

    match mode:
        case SyncMode.OVERRIDE:
            return target

        case SyncMode.INCREMENT:
            return _increment.unique_candidate(path=target, ensure_parent=True)

        case SyncMode.IGNORE:
            raise PathGuardError(PathGuardReason.SYNC, target=target)


#  LINE: -- Functors -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class TransferStrategy(SafeFunctor[[Path, Path], Path]):
    """Execute Transfer Operation in Safe Environment"""

    policy = PolicyField(ErrorPolicy.RE_RAISE)

    def __init__(self, **kwargs):
        kwargs.setdefault("error_policy", ErrorPolicy.RE_RAISE)
        super().__init__(**kwargs)

    check_sync_mode: Callable = staticmethod(check_sync_mode)

    def synced(self, source: Path, target: Path, mode: SyncMode) -> Path:
        """Apply SyncMode and Transfer Source to confirmed Target"""
        return self(source, check_sync_mode(target, mode))


class DeleteStrategy(SafeFunctor[[Path], bool]):
    """Execute Delete Operation in Safe Environment"""

    def on_error(self, error: Exception, target: PathArg) -> bool:
        # LATER: add some nice views! maybe to intermediate PathStrategy?
        logger.warning(f"{self.__name__}: {clsname(error)}", error, target)
        return False


#  LINE: -- Function Primitives -- -- - -- -- - -- -- - -- -- - -- -- - -- --


#  INFO: -- transfer -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _rotate(source: Path, target: Path) -> Path:
    """Move Source to Target and if reset: Create empty File or Dir"""
    return source.rename(target)


def _copy(source: Path, target: Path) -> Path:
    """Copy Source to Target"""
    return source.copy(target)


def _symlink(source: Path, target: Path) -> Path:
    """Create Absolute Symlink at Target Pointing to Source"""
    target.symlink_to(source)
    return target


def _hardlink(source: Path, target: Path) -> Path:
    """Create Hardlink at Target Pointing to Source"""
    target.hardlink_to(source)
    return target


def _handle_hardlink(error: Exception, source: Path, target: Path):
    if isinstance(error, OSError):
        raise PathGuardError(
            PathGuardReason.HARDLINK,
            source=source,
            target=target,
            caught=error,
        ) from error
    else:
        raise error


#  INFO: -- delete -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _remove(path: Path) -> None:
    if path.is_dir():
        import shutil  # LATER: upgrade with pathlib?

        shutil.rmtree(path)
    else:
        path.unlink()


def _trash(path: Path):
    from send2trash import send2trash

    send2trash(path)


#  LINE: -- Functor Instanciation -- -- - -- -- - -- -- - -- -- - -- -- - -- --


#  INFO: -- transfer -- -- - -- -- - -- -- - -- -- - -- -- - -- --


Symlink = TransferStrategy(
    name="PathGuard - Simlink",
    call=_symlink,
)
Copy = TransferStrategy(
    name="PathGuard - Copy",
    call=_copy,
)
Rotate: TransferStrategy = TransferStrategy(
    name="PathGuard - Rotate", call=_rotate
)
Hardlink = TransferStrategy(
    name="PathGuard - Hardlink",
    call=_hardlink,
    catch=_handle_hardlink,
)


#  INFO: -- delete -- -- - -- -- - -- -- - -- -- - -- -- - -- --


Remove = DeleteStrategy(
    name="PathGuard - Remove",
    call=_remove,
)
Trash = DeleteStrategy(
    name="PathGuard - Trash",
    call=_trash,
)


#  LINE: -- Assemble -- -- - -- -- - -- -- - -- -- - -- -- - -- --


#  INFO: -- transfer -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@castpath
def rotate(
    source: SourcePath,
    target: TargetPath,
    mode: SyncMode = SyncMode.INCREMENT,
    reset: bool = False,  # LATER: accept default file
) -> Path:

    is_directory: bool = source.is_dir()  # store for reset logic
    transferred: Path = Rotate.synced(source, target, mode=mode)

    if reset:
        if is_directory:
            source.mkdir()
        else:
            source.touch()

    return transferred


@castpath
def copy(
    source: SourcePath,
    target: TargetPath,
    mode: SyncMode = SyncMode.INCREMENT,
) -> Path:
    return Copy.synced(source, target, mode=mode)


@castpath
def symlink(
    source: ResolvedSource,
    target: TargetPath,
    mode: SyncMode = SyncMode.INCREMENT,
) -> Path:
    return Symlink.synced(source, target, mode=mode)


@castpath
def hardlink(
    source: SourcePath,
    target: TargetPath,
    mode: SyncMode = SyncMode.INCREMENT,
) -> Path:
    return Hardlink.synced(source, target, mode=mode)


#  INFO: -- delete -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def remove(target: TargetPath) -> bool:
    """Remove file or folder at target location"""
    return Remove(target)


def trash(target: TargetPath) -> bool:
    """Move file or folder at target location to system trash"""
    return Trash(target)


def prune(
    base_target: TargetPath, remaining: int = 5, *, use_trash: bool = False
) -> list[Path]:
    """Prune files of incremental PathName Sequence until remaining"""

    if len(sequence := _increment.find_sequence(base_target)) <= remaining:
        return []

    _prune_strategy = trash if use_trash else remove

    return [
        path  #
        for path in sequence[remaining:]
        if _prune_strategy(path)
    ]
