"""
Format and Parse Names in both directions

- NameParser: unified bidirectional __call__ (the stable root)

"""  # TODO: explain implementations

__all__: list[str] = [
    # base
    "NamePattern",  # TODO: needed 80% sure
    "NameParser",
    # implementations
    "ColoredName",
    "ParsedName",
    "SchemaName",
    "Name",  # TODO: needed 40% sure, just use utils.parse.name.name for this?
]

from .base import (
    NameParser,
    NamePattern,
)
from .colored import ColoredName
from .core import ParsedName
from .name import Name
from .schema import SchemaName
