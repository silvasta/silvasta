"""
The Builder (for classes)

- Collect ideas for compositions and provide implementation support

Infrastructure:
- Ghost: type check dummy

---

Strategy:
  Early
  - Protocol support for Builder
  - Consistent naming for builder: modules, functions, instances and classes
  - Basic infrastructur
  Later
  - Collect and show best working concepts
  Final
  - The Generalized Builder

"""

__all__: list[str] = [
    "Builder",
    "Constructor",
    "Injector",
    #
    "Ghost",
]

from ._core import Builder, Constructor, Injector
from ._ghost import Ghost
