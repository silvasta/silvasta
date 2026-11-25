"""
Provide pure functional fragments ready to use or assemble

- Detect, Inspect, Neglect, Modify, whatever...

                                   DependencyLevel.sstcore.brick[0]

"""

__all__: list[str] = [
    "clsname",
    "funcname",
    "objname",
    # modules
    "attr",
    "scan",
    "invoke",
    "typehint",
    "types",
    "sig",
    ## invoke
    "rich",
    "cli",
    "log",
    # check
    "is_private",
    "is_dunder",
    "is_protocol",
    "is_typing_generic",
    "is_variadic",
    "Visibility",
    #
    "AttrFilter",
]

# LATER: add dict::__dict__ again

from . import _attr as attr
from . import _invoke as invoke
from . import _scan as scan
from . import _sig as sig
from . import _typehint as typehint
from . import _types as types
from ._check import (
    Visibility,
    is_dunder,
    is_private,
    is_protocol,
    is_typing_generic,
    is_variadic,
)
from ._core import clsname, funcname, objname
from ._filter import AttrFilter
from ._invoke import cli, log, rich
