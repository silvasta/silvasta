"""
Implement the Variations and Extensions of the Core Registry

- Mix Register Variations and Extension as desired
- Combine with other Classes, BaseModel, ...

Info:
  - Register: Protocol definition, check and fulfill the Shape
  - Registry: Implementation approaches -> derive further
"""

__all__: list[str] = [
    "ListRegistry",
    "FilterRegistry",
    "DictRegistry",
    "TupleRegistry",
]

# NEXT: BisectRegistry

# LATER: FunctorRegistry

from ._dict import DictRegistry
from ._extras import FilterRegistry
from ._list import ListRegistry
from ._tuple import TupleRegistry
