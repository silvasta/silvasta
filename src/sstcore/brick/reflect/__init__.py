"""
Provide pure functional fragments ready to use or assemble

- Detect, Inspect, Neglect, Modify, whatever...

                                   DependencyLevel.sstcore.brick[0]

"""

__all__: list[str] = [
    # reflect
    "clsname",
    "funcname",
    "is_private",
    "is_dunder",
    "is_protocol",
    "is_private_not_calling",
    "is_typing_generic",
    # scan
    "data",
    "pydantic",
    "AttrFilter"
    # attr
    "attr",
    "_attr",
    "doc",
    "name",
    "text",
    # invoke
    "invoke",
    "_invoke",
    "rich",
    "cli",
    "log",
]

from . import _attr as attr  # noqa: F401
from . import _invoke as invoke
from ._attr import _attr
from ._core import (
    clsname,
    funcname,
    is_private_not_calling,
    is_protocol,
    is_typing_generic,
)
from ._invoke import _invoke
from ._scan import AttrFilter, data, pydantic  # noqa: F401

# TODO: Callable module trick, better for invoke() and invoke.xxx()
