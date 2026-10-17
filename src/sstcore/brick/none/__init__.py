"""
Nonething interesting to see here...

- Ghost: type check dummy
- ViewSentinel: none dummy for views
- sentinel: dispatch sentinel py315 and earlier

- UNSET: active sentinel intended for all public use

                                   DependencyLevel.sstcore.brick[0]
"""

__all__: list[str] = [
    "Ghost",
    "ViewSentinel",
    "sentinel",
    "UNSET",
]

from ._ghost import Ghost
from ._sentinel import UNSET, ViewSentinel, sentinel
