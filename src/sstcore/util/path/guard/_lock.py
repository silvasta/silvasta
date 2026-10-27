"""
Lock File Preparation

with PathGuard.lock(target) as path:
    ...

"""

# TODO: mount PathGuard.lock

import os
import time
from pathlib import Path

from ....brick.color import colorize
from ....brick.color.box import Colors
from ....error import PathGuardError, PathGuardReason
from ....port.link import PortEmit, tap
from ._arg import PathArg, PathSpec

c = Colors()


@tap.trace
class Lock:
    """Cross-process exclusive lock context using atomic O_CREAT | O_EXCL."""

    _debug: PortEmit

    def __init__(
        self,
        target: PathArg,  # LATER: accept spec, PathSpec or something else
        /,
        *,
        timeout: float = 5.0,
        poll_interval: float = 0.02,
    ) -> None:
        target: Path = PathSpec.ok(target, ensure_parent=True)
        self.lock_file: Path = target.with_name(f".{target.name}.lock")
        self.timeout: float = timeout
        self.poll_interval: float = poll_interval
        self.target: Path = target

    def __str__(self):
        return f"{type(self).__name__}[{self.lock_file}]"

    def __rich__(self):
        return f"{c.teal(type(self).__name__)}[{colorize.path(self.lock_file)}]"

    def __enter__(self) -> Path:
        start: float = time.monotonic()
        self._debug(f"Locking at : {time.monotonic()}")
        print(self._debug)

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

        if error is None:
            self._debug(f"End   : {time.monotonic()}")
        else:
            self._debug(f"{type(error).__name__}[{error}]")

        return False


if __name__ == "__main__":
    #
    #  LINE: -- Examples -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    class _PathG:
        Lock = Lock

    with _PathG.Lock(Path.cwd() / "my_file.md") as path:
        print(f"Inside: {time.monotonic()}")
        print(path)
