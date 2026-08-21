# IDEA: Builder[Class] and Constructor[Meta] here together
# - so far there is not a lot from meta -> 1 reason more to combine
# - instead of a split now and not very soon but when the port gets foldered,
#   they will anyway come again together
# TASK: find porper naming over both categories
# New Meta
# - construct Constructor -> meta builder
# - AI_QUESTION what else could be needed here??
# Existing class compose
# - Builder -> class builder
# - build -> mixins (maybe on top of some (mostly not standalone) base)
# - compose -> mixins + existing class or mixins
# - inject -> like compose but by decorator
# - compose -> so far the name of the module with the Builder
# other words for this context
# - Factory, produce -> clearly something for (massively) create instances
# - assemble, Assembler -> unsure maybe just as word for docstrings
"""
The Builder (for classes)

- Collect ideas for compositions and provide implementation support


---

Strategy:
  Early
  - Protocol support for Builder
  - Consistent naming for builder: modules, functions, instances and classes
  - Basic infrastructur
  Later
  - Collect and show best working concepts
  Final
  - The Generalized Builder (typed)

"""

__all__: list[str] = [
    "Builder",
    "Constructor",
    "Injector",
]

from ._core import Builder, Constructor, Injector
