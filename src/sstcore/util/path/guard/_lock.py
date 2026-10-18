"""
Lock File Preparation

with PathGuard.lock(target) as path:
    ...

"""

import os
import time
from contextlib import ContextDecorator
from pathlib import Path

from ....error import PathGuardError, PathGuardReason
from ._arg import ParentEnsuredPath, castpath

# NEXT: mount PathGuard.lock


@castpath
def lock(
    target: ParentEnsuredPath,
    *,
    timeout: float = 5.0,
    poll_interval: float = 0.02,
) -> _LockContext:
    """Acquire an exclusive sidecar file lock (.name.lock) and yield the Path."""
    return _LockContext(target, timeout=timeout, poll_interval=poll_interval)


class _LockContext(ContextDecorator):
    """Cross-process exclusive lock context using atomic O_CREAT | O_EXCL."""

    def __init__(
        self,
        target: Path,
        *,
        timeout: float = 5.0,
        poll_interval: float = 0.02,
    ) -> None:
        self.target: Path = target
        self.lock_file: Path = target.with_name(f".{target.name}.lock")
        self.timeout: float = timeout
        self.poll_interval: float = poll_interval

    def __enter__(self) -> Path:
        start = time.monotonic()

        while True:
            try:
                fd: int = os.open(
                    path=self.lock_file,
                    flags=os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    mode=0o600,
                )
                with os.fdopen(fd, "w") as f:
                    f.write(f"{os.getpid()}\n")

                return self.target

            except FileExistsError as error:
                if (time.monotonic() - start) >= self.timeout:
                    raise PathGuardError(
                        PathGuardReason.LOCK,
                        target=self.target,
                        lock_file=self.lock_file,
                        timeout=self.timeout,
                    ) from error
                time.sleep(self.poll_interval)

    def __exit__(self, _type, error, _traceback) -> bool:
        self.lock_file.unlink(missing_ok=True)

        if error is not None:
            print(f"{type(error).__name__}[{error}]")

        return False
