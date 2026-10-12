"""
Provide pure functional fragments ready to use or assemble

- Detect, Inspect, Neglect, Modify, whatever...

                                   DependencyLevel.sstcore.brick[0]

"""

__all__: list[str] = [
    # reflect
    "clsname",
    "funcname",
    "objname",
    # scan
    "data",
    "pydantic",
    # check
    "AttrFilter",
    "is_private",
    "is_dunder",
    "is_protocol",
    "is_private_not_calling",
    "is_typing_generic",
    # attr
    "attr",
    "_attr",
    "doc",
    "module",
    "name",
    "text",
    # invoke
    "invoke",
    "_invoke",
    "rich",
    "cli",
    "log",
]

# IDEA: make __core__ == CallableModule.__call__
# define it only once, on the module class,
# - apply it from there :D

from . import _attr as attr
from . import _invoke as invoke
from ._attr import doc, module, name, text
from ._check import (
    AttrFilter,
    is_dunder,
    is_private,
    is_private_not_calling,
    is_protocol,
    is_typing_generic,
)
from ._core import clsname, funcname, objname
from ._scan import data, pydantic
