"""
Provide Base Components to create Views

- cli    __cli__
- string __str__
- rich   __rich__
- repr   __repr__
- log    __log__

Exploit shared patterns through common fundamentals:
- str and rich: (colored) name
- repr and log: structured data for text or json

Work out individual ideas while building toward a common brand.

"""

__all__: list[str] = [
    "cli",
    "string",
    "rich",
    "repr",
    "log",
    "MixinSentinel",
]

from . import _cli as cli
from . import _log as log
from . import _repr as repr
from . import _rich as rich
from . import _str as string
from ._basics import MixinSentinel
