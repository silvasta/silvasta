"""
Replace None

- until py315

Usage:
from sstcore.brick.none import sentinel
MISSING = sentinel("MISSING")
"""

__all__: list[str] = [
    "ViewSentinel",
    "sentinel",
]

import sys
from typing import Any

from ...port.calling import Richable
from ...port.event.dto import CliDTO, LogDTO


class ViewSentinel:
    """Imitate ViewMixin to replace None in View selection pipeline"""

    # NOTE: what about __str|repr__?

    def __cli__(self) -> CliDTO:
        raise NotImplementedError

    def __log__(self) -> LogDTO:
        raise NotImplementedError

    def __rich__(self) -> Richable:
        raise NotImplementedError


#  INFO: -- Experimental -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def use_latest_features() -> bool:
    """Next type check dummy, avoiding greying out..."""
    return sys.version_info >= (3, 15)


if use_latest_features():
    import builtins

    sentinel = builtins.sentinel
else:

    def sentinel(name: str, repr: str | None = None) -> Any:
        """Imitate the new sentinel class in py314-"""

        class Sentinel:
            def __repr__(self) -> str:
                return repr if repr is not None else f"<{name}>"

            def __bool__(self) -> bool:
                return True

        Sentinel.__name__ = name
        return Sentinel()
