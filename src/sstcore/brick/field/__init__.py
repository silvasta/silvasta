"""
Class attribute Fields

- Attach with Descriptor
"""

__all__: list[str] = [
    # base
    "NamedField",
    "ReadField",
    "WriteField",
    "DeleteField",
    # extension
    "ResetField",
    "ValidField",
    "TypedField",
    "EmitField",
    "ConfigField",
    # composed
    "Injected",
    "Collected",
    "Derived",
    "Forward",
]

from ._base import (
    ConfigField,
    DeleteField,
    EmitField,
    NamedField,
    ReadField,
    ResetField,
    TypedField,
    ValidField,
    WriteField,
)
from ._core import Collected, Derived, Forward, Injected
