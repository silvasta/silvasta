"""
Produce the Components for the Dot-Accessed Typed Stacking

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

from ._core import StackBase as StackBase
from ._core import StackCore as StackCore
from ._core import StackLayer as StackLayer
from ._core import StackRunner as StackRunner
from ._core import StackState as StackState
from ._stubs._ansi import AnsiEmpty as AnsiStack
from ._stubs._random import RandomEmpty as RandomStack
from ._stubs._text import TextEmpty as TextStack

DTO_STACK: RandomStack
ANSI_STACK: AnsiStack
STRING_STACK: TextStack

# INFO: use this for more dynamic escape hatch
# from typing import Any as _Any
# def __getattr__(name: str) -> _Any:
