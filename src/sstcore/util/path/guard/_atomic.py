"""
File System Operations (Atomic & SafeFunctor-backed)

- Lock: cross-process exclusive lockfile context manager
- Transfer: from source to target (Rotate, Copy, Symlink, Hardlink)
- Delete: from target to ... (Remove, Trash, Prune)

                         DependencyLevel.sstcore.util.path.guard[3]
"""

# IMPORTANT: compare this with Functor and the existing ._operate
# TASK: find solution that combines best of both!!!

__all__: list[str] = [
    "TransferStrategy",
    "check_sync_mode",
    "DeleteStrategy",
    # transfer functors
    "Rotate",
    "Copy",
    "Symlink",
    "Hardlink",
    # delete functors
    "Remove",
    "Trash",
    # transfer functions
    "rotate",
    "copy",
    "hardlink",
    "symlink",
    # delete functions
    "remove",
    "trash",
    "prune",
]

import errno
import os
import shutil
import uuid
from collections.abc import Callable
from pathlib import Path

from loguru import logger

from ....brick.field import PolicyField
from ....brick.reflect import clsname
from ....error import PathGuardError, PathGuardReason
from ....forge.func import SafeFunctor
from ....port.files import SyncMode
from ....port.functorial import ErrorPolicy
from . import _ensure, _increment, _lock
from ._arg import PathArg, ResolvedSource, SourcePath, TargetPath, castpath


def check_sync_mode(target: TargetPath, mode: SyncMode) -> Path:
    """Provide SyncMode Path that is valid to write or Raise"""

    if not target.exists():
        return _ensure._dir_logic(target.parent)

    match mode:
        case SyncMode.OVERRIDE:
            return target

        case SyncMode.INCREMENT:
            return _increment.unique_candidate(target, ensure_parent=True)

        case SyncMode.IGNORE:
            raise PathGuardError(PathGuardReason.SYNC, target=target)


#  LINE: -- Functors -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _temp_sibling(target: Path) -> Path:
    """Generate a unique temporary sibling path in the same directory (same FS)."""
    token: str = uuid.uuid4().hex[:8]
    return target.with_name(f".{target.name}.{os.getpid()}.{token}.tmp")


class TransferStrategy(SafeFunctor[[Path, Path], Path]):
    """
    Execute Transfer Operation in Safe Environment with OS-atomic SyncMode loop.

    The wrapped `func(source, candidate)` must perform an *exclusive* creation
    at `candidate` (raising `FileExistsError` if `candidate` already exists).
    """

    policy = PolicyField(ErrorPolicy.RE_RAISE)

    def __init__(
        self,
        *,
        override_func: Callable[[Path, Path], Path] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        # NEXT: check if that is not completely away from the Functor concept
        self.override_func: Callable[[Path, Path], Path] | None = override_func

    def _atomic_override(self, source: Path, target: Path) -> Path:
        """Atomically overwrite `target` using `override_func` or temp-sibling + `os.replace`."""

        tmp_target: Path = _temp_sibling(target)
        try:
            self(source, tmp_target)
            os.replace(tmp_target, target)
            return target
        except BaseException:
            tmp_target.unlink(missing_ok=True)
            raise

    def synced(self, source: Path, target: Path, mode: SyncMode) -> Path:
        """Apply SyncMode atomically and transfer `source` to confirmed `target`."""
        _ensure._dir_logic(target.parent)

        if mode is SyncMode.OVERRIDE:
            if target.exists():
                logger.warning(f"Overriding existing Path at {target=}")
            return self._atomic_override(source, target)

        # NEXT: why is this specific logic here in the base???
        for candidate in _increment.iter_unique_candidates(
            target, include_base=True
        ):
            try:
                transferred: Path = self(source, candidate)
                if candidate != target:
                    logger.info(f"Incremented atomically: {candidate.name}")
                return transferred
            except FileExistsError as error:
                if mode is SyncMode.IGNORE:
                    raise PathGuardError(
                        PathGuardReason.SYNC,
                        target=candidate,
                        sync_mode=mode.value,
                    ) from error
                continue

        raise RuntimeError("Unreachable: infinite candidate generator")


class DeleteStrategy(SafeFunctor[[Path], bool]):
    """Execute Delete Operation in Safe Environment"""

    def on_error(self, error: Exception, target: PathArg) -> bool:
        logger.warning(f"{self.__name__}: {clsname(error)}", error, target)
        return False


#  LINE: -- Function Primitives (Exclusive Creation) -- -- - -- -- - -- --


def _copy_excl(source: Path, candidate: Path) -> Path:
    """Copy `source` to `candidate` exclusively (raises FileExistsError if candidate exists)."""
    if source.is_dir():
        with _lock.Lock(candidate):
            if candidate.exists():
                raise FileExistsError(
                    errno.EEXIST, "Directory exists", str(candidate)
                )
            shutil.copytree(source, candidate)
            return candidate

    fd: int = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        with os.fdopen(fd, "wb") as dst, open(source, "rb") as src:
            shutil.copyfileobj(src, dst)
        shutil.copystat(source, candidate)
        return candidate
    except BaseException:
        candidate.unlink(missing_ok=True)
        raise


def _rotate_excl(source: Path, candidate: Path) -> Path:
    """Move `source` to `candidate` exclusively (raises FileExistsError if candidate exists)."""
    if source.is_dir():
        with _lock.Lock(candidate):
            if candidate.exists():
                raise FileExistsError(
                    errno.EEXIST, "Directory exists", str(candidate)
                )
            shutil.move(str(source), str(candidate))
            return candidate

    try:
        os.link(source, candidate)
        source.unlink()
        return candidate
    except FileExistsError:
        raise
    except OSError as error:
        if error.errno in (errno.EXDEV, errno.EPERM, errno.ENOTSUP):
            logger.debug("Fallback to atomic copy+unlink for rotate.")
            _copy_excl(source, candidate)
            source.unlink()
            return candidate
        raise


def _rotate_override(source: Path, target: Path) -> Path:
    """Fast-path atomic override for Rotate using os.replace."""
    try:
        os.replace(source, target)
        return target
    except OSError as error:
        if error.errno == errno.EXDEV:
            tmp_target = _temp_sibling(target)
            try:
                _copy_excl(source, tmp_target)
                os.replace(tmp_target, target)
                source.unlink()
                return target
            except BaseException:
                tmp_target.unlink(missing_ok=True)
                raise
        raise


def _symlink_excl(source: Path, candidate: Path) -> Path:
    """Create Symlink at `candidate` pointing to `source` (natively exclusive)."""
    candidate.symlink_to(source)
    return candidate


def _hardlink_excl(source: Path, candidate: Path) -> Path:
    """Create Hardlink at `candidate` pointing to `source` (natively exclusive)."""
    candidate.hardlink_to(source)
    return candidate


def _handle_hardlink(error: Exception, source: Path, target: Path):
    if isinstance(error, FileExistsError):
        raise error
    if isinstance(error, OSError):
        raise PathGuardError(
            PathGuardReason.HARDLINK,
            source=source,
            target=target,
            caught=error,
        ) from error
    raise error


#  INFO: -- delete -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _remove(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def _trash(path: Path) -> None:
    from send2trash import send2trash

    send2trash(path)


#  LINE: -- Functor Instantiation -- -- - -- -- - -- -- - -- -- - -- --


Symlink = TransferStrategy(
    name="PathGuard - Symlink",
    func=_symlink_excl,
)
Copy = TransferStrategy(
    name="PathGuard - Copy",
    func=_copy_excl,
)
Rotate = TransferStrategy(
    name="PathGuard - Rotate",
    func=_rotate_excl,
    override_func=_rotate_override,
)
Hardlink = TransferStrategy(
    name="PathGuard - Hardlink",
    func=_hardlink_excl,
    catch=_handle_hardlink,
)

Remove = DeleteStrategy(
    name="PathGuard - Remove",
    func=_remove,
)
Trash = DeleteStrategy(
    name="PathGuard - Trash",
    func=_trash,
)


#  LINE: -- Assemble Public Functions -- -- - -- -- - -- -- - -- --


@castpath
def rotate(
    source: SourcePath,
    target: TargetPath,
    mode: SyncMode = SyncMode.INCREMENT,
    reset: bool = False,
) -> Path:
    is_directory: bool = source.is_dir()
    transferred: Path = Rotate.synced(source, target, mode=mode)

    if reset:
        if is_directory:
            source.mkdir(parents=True, exist_ok=True)
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


@castpath
def remove(target: TargetPath) -> bool:
    """Remove file or folder at target location"""
    return Remove(target)


@castpath
def trash(target: TargetPath) -> bool:
    """Move file or folder at target location to system trash"""
    return Trash(target)


@castpath
def prune(
    base_target: TargetPath, remaining: int = 5, *, use_trash: bool = False
) -> list[Path]:
    """Prune files of incremental PathName Sequence until remaining"""

    if len(sequence := _increment.find_sequence(base_target)) <= remaining:
        return []

    _prune_strategy = trash if use_trash else remove

    return [path for path in sequence[remaining:] if _prune_strategy(path)]
