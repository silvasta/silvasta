"""
Collect Callables ready to assembe on Calling Objects

                                  DependencyLevel.sstcore.brick[0]
"""

from typing import TYPE_CHECKING

__all__: list[str] = [
    "dto1",
]

from ._example import dto_stack

# AI: version1 - failed import...
# from ._stub import GreeterEmpty


# AI: version2 - works a bit further...
if TYPE_CHECKING:
    from ._stub import GreeterEmpty

    dto1: GreeterEmpty = dto_stack
else:
    dto1 = dto_stack
