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
    "Ghost",
]

from ._ghost import Ghost

# NEXT: name brainstorming:
# verbs
# - assemble
# - build
# - compose
# - inject
# - construct
# nouns
# - factory
