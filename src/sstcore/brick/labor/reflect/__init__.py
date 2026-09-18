"""
Inspect arbitrary objects and safely pull out specific attributes

                                                           ModuleLevel[0]
"""

__all__: list[str] = [
    # IDEA: name: cls?
    "clsname",
    "data",
    "pydatic",
    "_dict",
    #
    "dig",  # WARN: name overlap, use ._dig.dig as __call__??
    "name",
    "text",
    "func",
    #
    "invoke",
    "rich",
    "cli",
    "log",
]

from . import _dig as dig
from ._dig import func, name, text
from ._invoke import cli, invoke, log, rich
from ._reflect import _dict, clsname, data, pydatic
