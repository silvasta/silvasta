"""
WRITE FINAL STACK HERE

- Temporary until ready to move to proper place

"""

# NEXT: implement

from typing import TYPE_CHECKING

__all__: list[str] = [
    "StackingData",
    "StackingCore",
]

from .___DEFINE import Stack, Stacking

#  LINE: -- Single -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class StackingData: ...


if TYPE_CHECKING:
    _unit: Stacking = StackingData()
    _cls: type[Stacking] = StackingData


#  LINE: -- Combination -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class StackingCore: ...


if TYPE_CHECKING:
    _unit: Stack = StackingCore()
    _cls: type[Stack] = StackingCore
