"""
Provide pure functional fragments ready to use or assemble

- Detect, Inspect, Neglect, Modify, whatever...

                                   DependencyLevel.sstcore.brick[0]

"""

__all__: list[str] = [
    # single
    "just_return",
    "validate_signature",
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
    # mutate
    "mutate",
]


from . import _mutate as mutate
from . import _reflect as reflect
from . import _scan as scan
from ._collection import just_return
from ._inspect import validate_signature
from ._invoke import cli, invoking, log, rich
from ._reflect import clsname, funcname, name, reflecting, text
from ._scan import data, pydantic
