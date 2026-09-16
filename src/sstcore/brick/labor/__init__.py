"""
Provide pure functional fragments ready to use or assemble

- Detect, Inspect, Neglect, Modify, whatever...
                                                 DependencyLevel[0]

"""

__all__: list[str] = [
    "mro",
    "reflect",
    "inject",
    # single
    "clsname",
    "just_return",
]


from . import _inject as inject
from . import mro, reflect
from ._inject import just_return
from .reflect import clsname
