"""
Collect Stubs for Stacking

-
"""

from ...port.stacking import (
    RunningStack,
    StackingCore,
    StackingLayer,
    StackingState,
)
from ._stubs._format import FormatEmpty
from ._stubs._printer import PrinterEmpty
from ._stubs._random import GreeterEmpty

StackLayer: StackingLayer
StackCore: StackingCore
StackRunner: RunningStack
StackState: StackingState

DTO_STACK: GreeterEmpty
ANSI_STACK: PrinterEmpty
STRING_STACK: FormatEmpty

# NOTE: The __getattr__ Escape Hatch:
# To prevent accidental strict shadowing of untyped
# dynamic utilities within the same module, include:
#   def __getattr__(name: str) -> Any: ...
# at the bottom of your generated __init__.pyi.
# This explicitly tells the type checker to allow dynamic
# lookups for anything not explicitly defined in the stub,
# preventing false-positive errors across the library.
