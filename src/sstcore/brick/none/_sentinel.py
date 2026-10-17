"""
Replace None and Any with type safe Replacement

- Avoid Any to erasure the type just for widening the annotation
- Avoid None as unprecise and unpredictable placeholder

Use the UNSET Sentinel as Value and as Type!
- number: int | UNSET = UNSET
- clearly narrows the type afterwards,
  like after isinstance(number,int) == False
  -> number clearly identified as UNSET

                              DependencyLevel.sstcore.brick.none[0]
"""

__all__: list[str] = [
    "UNSET",
    "sentinel",
    "ViewSentinel",
]

import sys
from pathlib import Path

from ...port.event.dto import CliDTO, LogDTO
from ...port.represent import Richable


class ViewSentinel:
    """Imitate ViewMixin to replace None in View selection pipeline"""

    def __cli__(self) -> CliDTO:
        raise NotImplementedError

    def __log__(self) -> LogDTO:
        raise NotImplementedError

    def __rich__(self) -> Richable:
        raise NotImplementedError


if sys.version_info >= (3, 15):
    import builtins

    sentinel = builtins.sentinel

else:
    import typing_extensions

    sentinel = typing_extensions.sentinel

UNSET = sentinel("UNSET")


if __name__ == "__main__":
    #
    #  LINE: -- Tests -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    print(f"Sentinel {sys.version_info} prepared: {sentinel}")

    def _narrow_type(path: Path | UNSET = UNSET):
        from typing import reveal_type

        if path is UNSET:
            reveal_type(path)
        else:
            reveal_type(path)

    print(UNSET)
    print("\n", "repr:")
    print(repr(UNSET))
    print("\n", "dir:")
    print(dir(UNSET))
