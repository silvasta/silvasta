"""
Normalize the input and make it ready for process

- Sanitize, Ensure or Reject
                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "transform"
    #
    "dict_to_str",
    "dict_to_list",
    "list_to_str",
    "impossible_brackets",
    "format_kv",
]

from . import _transform as transform
from ._transform import (  # TODO: Filter!
    dict_to_list,
    dict_to_str,
    format_kv,
    impossible_brackets,
    list_to_str,
)
