"""
One switch, many probes.

Off: boolean test, no rich import, no I/O.
On:  rich.print, optional channel filter.
The flag is read at call time, so opt-in does not require rebinding.

Sits in port so brick and forge share it without a back-edge.
"""

from __future__ import annotations

from functools import wraps

__all__: list[str] = [
    "dbg",
    "DebugGate",
]

import os
import sys
from contextvars import ContextVar
from typing import Any

_ON = frozenset({"1", "true", "on", "yes", "all", "*"})
_OFF = frozenset({"", "0", "false", "off", "no"})
_busy: ContextVar[bool] = ContextVar("sstcore_dbg_busy", default=False)


def _from_env(raw: str | None) -> tuple[bool, frozenset[str]]:
    # EXTRACT:
    if raw is None or raw.strip().lower() in _OFF:
        return False, frozenset()
    key = raw.strip().lower()
    if key in _ON:
        return True, frozenset()
    return True, frozenset(
        part.strip() for part in raw.split(",") if part.strip()
    )


class DebugGate:
    """Call-time debug sink. Pass channel as a keyword: dbg('msg', ch='vault')."""

    __slots__ = ("enabled", "channels")

    def __init__(self) -> None:
        self.enabled, self.channels = _from_env(
            os.environ.get("SSTCORE_DEBUG")
        )

    def on(self, *channels: str) -> None:
        self.enabled = True
        self.channels = frozenset(channels)

    def off(self) -> None:
        self.enabled = False

    def hot(self, ch: str = "") -> bool:
        # EXTRACT:
        """True when a probe in this channel would print. Guard expensive messages."""
        if not self.enabled:
            return False
        if not self.channels or not ch:
            return True
        return ch in self.channels

    def __bool__(self) -> bool:
        return self.enabled

    def __call__(self, *args: Any, ch: str = "", **_ignored: Any) -> None:
        if not self.hot(ch) or _busy.get():
            return
        token = _busy.set(True)
        try:
            from rich import print as rprint

            if ch:
                args = (f"[dim]{ch}[/]", *args)
            rprint(*args)
        except Exception as exc:
            # EXTRACT:
            sys.stderr.write(f"[dbg] {type(exc).__name__}: {exc}\n")
        finally:
            _busy.reset(token)


dbg = DebugGate()


def watch(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if dbg:
            dbg(f"→ {fn.__qualname__}", ch="call")
        return fn(*args, **kwargs)

    return wrapper


if __name__ == "__main__":
    ...
    palette = "palette"
    dbg(f"palette ready: {palette!r}", ch="color")

    self = dbg
    if dbg.hot("vault"):
        dbg(f"End of Init: {self!r}", ch="vault")
