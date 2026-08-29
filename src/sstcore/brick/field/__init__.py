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
    "ValidField",
    "EmitField",
    "ConfigField",
    # composed
    "Injected",
    "Collected",
    "Derived",
    "Format",
]

from ._base import (
    ConfigField,
    DeleteField,
    EmitField,
    NamedField,
    ReadField,
    ValidField,
    WriteField,
)
from ._core import (
    Collected,
    Derived,
    Format,
    Injected,
)
