"""
Provide pure functional fragments ready to use or assemble

- Detect, Inspect, Neglect, Modify, whatever...

                                   DependencyLevel.sstcore.brick[0]

"""

__all__: list[str] = [
    # reflect
    "clsname",
    "funcname",
    "reflect",
    "reflecting",
    ## subfunctions might be containered
    "doc",
    "name",
    "text",
    # invoke
    "invoke",
    "invoking",
    ## subfunctions might be containered
    "rich",
    "cli",
    "log",
    # scan
    "scan",
    ## subfunctions might be containered
    "data",
    "pydantic",
]


from . import _invoke as invoke
from . import _reflect as reflect
from . import _scan as scan
from ._invoke import cli, invoking, log, rich
from ._reflect import clsname, funcname, name, reflecting, text
from ._scan import data, pydantic
