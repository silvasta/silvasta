"""
Collect Callables ready to assembe on Calling Objects

                                   DependencyLevel.sstcore.brick[1]
"""

__all__: list[str] = [
    "StackBase",
    "StackLayer",
    "StackCore",
    "StackState",
    "StackRunner",
    # examples
    "ANSI_STACK",
    "DTO_STACK",
    "STRING_STACK",
]

from ._example import ANSI_STACK, DTO_STACK, STRING_STACK
from ._stack import StackBase, StackCore, StackLayer, StackRunner, StackState
