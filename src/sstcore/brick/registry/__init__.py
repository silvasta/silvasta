"""
Implement the Variations and Extensions of the Core Registry

- Mix Register Variations and Extension as desired
- Combine with other Classes, BaseModel, ...

Info:
  - Register: Protocol definition, check and fulfill the Shape
  - Registry: Implementation approaches -> derive further
"""

# IMPORTANT: check again the name...
# /󰉋 /color
# /󰉋 /forge
# /󰉋 /format
# /󰉋 /func
# /󰉋 /meta
# /󰉋 /name
# /󰉋 /none
# /󰉋 /registry # Somehow Outlier... ideas?
# /󰉋 /view
# /󰌠 /time.py
# IDEAS: name of registry
# - [X] Rating (5 best to 0)
# - [4] order
# - [3] sort
# - [0] data
# - [2] box

__all__: list[str] = [
    "ListRegistry",
    "FilterRegistry",
    "DictRegistry",
    "TupleRegistry",
]

from ._dict import DictRegistry
from ._extend import FilterRegistry
from ._extend import FunctorRegistry as _FunctorRegistry
from ._list import ListRegistry
from ._tuple import TupleRegistry

_TODO = _FunctorRegistry
