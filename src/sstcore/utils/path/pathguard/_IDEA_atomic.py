import os
import shutil
import time
from contextlib import contextmanager
from pathlib import Path

from loguru import logger

from ....exceptions import PathGuardError, PathGuardReason
from ._input import PathInput, PathSpec
from ._operate import SyncMode


@contextmanager
def _sync_lock(target: Path):  # TODO: with PathGuard.lock(ed|ing):
    """
    Cross-process atomic lock

    revent TOCTOU race conditions during file evaluation and transfer.
    """
    # Create a hidden lockfile based on the base target name
    lock_file = target.parent / f".{target.name}.lock"

    while True:
        try:
            # os.O_CREAT | os.O_EXCL ensures atomic creation.
            # It fails immediately if the file already exists.
            fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            # Another process holds the lock; wait and retry
            time.sleep(0.02)

    try:
        yield
    finally:
        # Always release the lock, even if the operation crashes
        lock_file.unlink(missing_ok=True)


@contextmanager
def lock(target: PathInput, timeout: float = 5.0):
    """Public context manager for safe Read-Modify-Write cycles."""
    target_path = PathSpec.ok(target)
    lock_file = target_path.with_name(f".{target_path.name}.lock")

    start_time = time.time()
    while True:
        try:
            # Try to exclusively create the lock file
            fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError as e:
            if time.time() - start_time > timeout:
                raise PathGuardError(
                    f"Timeout waiting to lock {target_path}"
                ) from e
            time.sleep(0.05)

    try:
        yield target_path
    finally:
        lock_file.unlink(missing_ok=True)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Mostly Atomic
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def _atomic_copy_increment(source: Path, target: Path) -> Path:
    """Increment target name and copy atomically to prevent race conditions."""

    suffixes: str = "".join(target.suffixes)
    original_stem: str = (
        target.name[: -len(suffixes)] if suffixes else target.name
    )
    parent: Path = target.parent
    counter = 1

    while True:
        candidate = parent / f"{original_stem}_{counter}{suffixes}"
        try:
            # Atomic creation: fails instantly if candidate exists
            fd = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY)

            # If we get here, we own the file. Stream the data into it.
            with os.fdopen(fd, "wb") as dst:
                with open(source, "rb") as src:
                    shutil.copyfileobj(src, dst)

            logger.info(f"Incremented atomically: {candidate.name}")
            return candidate

        except FileExistsError:
            # Another process took this name. Increment and try again.
            counter += 1


def _atomic_move_increment(source: Path, target: Path) -> Path:
    """Increment target name and move atomically using hardlinks."""

    suffixes: str = "".join(target.suffixes)
    original_stem: str = (
        target.name[: -len(suffixes)] if suffixes else target.name
    )
    parent: Path = target.parent
    counter = 1

    while True:
        candidate = parent / f"{original_stem}_{counter}{suffixes}"
        try:
            # os.link fails atomically if candidate already exists
            os.link(source, candidate)

            # If the link succeeded, delete the original to complete the "move"
            source.unlink()

            logger.info(f"Rotated atomically: {candidate.name}")
            return candidate

        except FileExistsError:
            counter += 1

        except OSError as e:
            # Fallback for Cross-Device links (hardlinks only work on the same drive)
            if e.errno == 18:  # EXDEV: Cross-device link
                logger.debug(
                    "Cross-device move detected. Falling back to atomic copy+delete."
                )
                final_target = _atomic_copy_increment(source, target)
                source.unlink()
                return final_target
            raise e


def _copy(
    source: PathInput,
    target: PathInput,
    sync_mode: str | SyncMode = "increment",
) -> Path:
    """Copy Source to Target"""

    _source: Path = PathSpec.ok(source, must_exists=True)
    _target: Path = PathSpec.ok(target)
    sync_mode = SyncMode(sync_mode)

    if not _target.exists():
        _target.parent.mkdir(parents=True, exist_ok=True)
        # Assuming safe to copy if it doesn't exist at first check.
        # (For absolute strictness, you could wrap this in O_EXCL too).
        import shutil

        shutil.copy2(_source, _target)
        return _target

    match sync_mode:
        case SyncMode.OVERRIDE:
            logger.warning(f"Overriding existing File at {_target=}")
            import shutil

            shutil.copy2(_source, _target)
            return _target

        case SyncMode.INCREMENT:
            # Hand off to the atomic increment loop
            return _atomic_copy_increment(_source, _target)

        case SyncMode.IGNORE:
            from ....exceptions import PathGuardError, PathGuardReason

            raise PathGuardError(
                reason=PathGuardReason.SYNC,
                target=_target,
                sync_mode="IGNORE",
            )


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### ATOMIC
### ATOMIC
### ATOMIC
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def _copy(
    source: PathInput,
    target: PathInput,
    sync_mode: str | SyncMode = "increment",
) -> Path:
    """Copy Source to Target with strict OS-level atomicity."""

    _source: Path = PathSpec.ok(source, must_exists=True)
    _target: Path = PathSpec.ok(target)
    sync_mode = SyncMode(sync_mode)

    _target.parent.mkdir(parents=True, exist_ok=True)

    # OVERRIDE doesn't care if the file exists, so we bypass O_EXCL.
    # shutil.copy2 silently and safely overwrites.
    if sync_mode == SyncMode.OVERRIDE:
        logger.warning(f"Overriding existing File at {_target=}")
        shutil.copy2(_source, _target)
        return _target

    # For INCREMENT and IGNORE, we use the Try-and-React loop
    suffixes: str = "".join(_target.suffixes)
    original_stem: str = (
        _target.name[: -len(suffixes)] if suffixes else _target.name
    )
    counter = 0

    while True:
        # counter == 0 attempts the exact base target first
        candidate = (
            _target
            if counter == 0
            else _target.parent / f"{original_stem}_{counter}{suffixes}"
        )

        try:
            # os.O_EXCL ensures this raises FileExistsError if the file was created
            # by another process even a nanosecond before this line runs.
            fd = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY)

            with os.fdopen(fd, "wb") as dst:
                with open(_source, "rb") as src:
                    shutil.copyfileobj(src, dst)

            # Preserve permissions and metadata like shutil.copy2 does
            shutil.copystat(_source, candidate)

            if counter > 0:
                logger.info(f"Incremented atomically: {candidate.name}")
            return candidate

        except FileExistsError as error:
            if sync_mode == SyncMode.IGNORE:
                raise PathGuardError(
                    reason=PathGuardReason.SYNC,
                    target=candidate,
                    sync_mode="IGNORE",
                ) from error
            # SyncMode is INCREMENT. Increment the counter and try again.
            counter += 1


def _rotate(
    source: PathInput,
    target: PathInput,
    sync_mode: str | SyncMode = "increment",
    reset: bool = False,
) -> Path:
    """Move Source to Target with strict OS-level atomicity."""

    _source: Path = PathSpec.ok(source, must_exists=True)
    _target: Path = PathSpec.ok(target)
    sync_mode = SyncMode(sync_mode)

    _target.parent.mkdir(parents=True, exist_ok=True)
    is_directory = _source.is_dir()

    if sync_mode == SyncMode.OVERRIDE:
        logger.warning(f"Overriding existing File at {_target=}")
        os.replace(_source, _target)  # os.replace is an atomic overwrite
        inspected_target = _target
    else:
        suffixes: str = "".join(_target.suffixes)
        original_stem: str = (
            _target.name[: -len(suffixes)] if suffixes else _target.name
        )
        counter = 0

        while True:
            candidate = (
                _target
                if counter == 0
                else _target.parent / f"{original_stem}_{counter}{suffixes}"
            )
            try:
                # os.link fails atomically if candidate already exists
                os.link(_source, candidate)
                _source.unlink()

                if counter > 0:
                    logger.info(f"Rotated atomically: {candidate.name}")

                inspected_target = candidate
                break

            except FileExistsError as e:
                if sync_mode == SyncMode.IGNORE:
                    raise PathGuardError(
                        reason=PathGuardReason.SYNC,
                        target=candidate,
                        sync_mode="IGNORE",
                    ) from e
                counter += 1
            except OSError as e:
                if e.errno == 18:  # EXDEV: Cross-device link
                    logger.debug(
                        "Cross-device move detected. Falling back to copy+delete."
                    )
                    # Pass off to the atomic copy we just built
                    inspected_target = _copy(_source, candidate, sync_mode)
                    _source.unlink()
                    break
                raise PathGuardError(
                    reason=PathGuardReason.HARDLINK,
                    target=candidate,
                    source=_source,
                ) from e

    if reset:
        if is_directory:
            _source.mkdir()
        else:
            _source.touch()

    return inspected_target
