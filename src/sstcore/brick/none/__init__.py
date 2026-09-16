"""
Nonething interesting to see here...

- Ghost: type check dummy
- ViewSentinel: none dummy

"""

__all__: list[str] = [
    "Ghost",
    # for the catalogue
    "ViewSentinel",
    # experiment
    "sentinel",
]

from ._ghost import Ghost
from ._sentinel import ViewSentinel, sentinel
