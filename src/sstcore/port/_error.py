"""
Specify SstCoreError before SstError is ready

- Temporary Location - where to go with that?
- Let's see when Raiser is ready...

                                    DependencyLevel.sstcore.port[3]
"""


# IMPORTANT: Global strategy, sync with sstcore.error

__all__: list[str] = [
    "EnumError",
    #
    "FailedDispatchError",
    "FailedHackError",
]

from enum import Enum
from typing import Any

from .raising import SstCoreError
from .solid import BaseEnum


class EnumError(SstCoreError, TypeError):
    """Temporary Resolve the SstEnumMeta blinding"""

    def __init__(
        self, member_or_cls: Enum | type[Enum], /, reason="", *args
    ) -> None:
        """Forward Args to Exception"""
        reason: str = reason or "Failed"
        match BaseEnum.membership(member_or_cls):
            case ():
                who = f"Unknown: {member_or_cls=}"
            case (enum_cls,):
                self.enum: type[BaseEnum] = enum_cls
                who = f"BaseEnum: {enum_cls}"
            case (enum_cls, member):
                self.enum: type[BaseEnum] = enum_cls
                self.member: BaseEnum = member
                who = f"BaseEnum: {enum_cls=}, {member=}"
        super().__init__(f"{who} | {reason=}", *args)


class FailedDispatchError(SstCoreError, NotImplementedError):  # MOVE: ._error?
    # TASK: sync with NotImplementedDispatchError
    """Raise on missing TargetType for singledispatch(method)"""

    def __init__(self, first: Any, *args: Any, **kwargs):
        self.first = first
        msg = f"Missing dispatch target for {type(first).__name__}"
        super().__init__(msg, *(first, *args), **kwargs)


class FailedHackError(SstCoreError):
    """
    It was a nice try, but...

    (I hope I don't have to  explain that this is mostly for internal tests...)
    """

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__("...I told you it will fail!", *args)
