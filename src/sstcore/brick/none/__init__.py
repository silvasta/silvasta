"""
Nonething interesting to see here...

- Ghost: type check dummy
- ViewSentinel: none dummy
  sentinel: dispatch sentinel py315 and earlier
                                                 DependencyLevel[0]
"""

# IMPORTANT: check naming conflict with .norm
# - decide if and how to keep this here
# don't import the Ghost instead of the InputSanitizer
# IDEA: brick.tool.none with brick.tool as new container for ... ?

__all__: list[str] = [
    "Ghost",
    "ViewSentinel",
    "sentinel",
]

from ._ghost import Ghost
from ._sentinel import ViewSentinel, sentinel
