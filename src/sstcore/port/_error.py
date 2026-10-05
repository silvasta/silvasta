"""
Specify SstCoreError before SstError is ready

- Temporary Location - where to go with that?
- Let's see when Raiser is ready...

                                    DependencyLevel.sstcore.port[2]
"""

__all__: list[str] = [
    "FailedDispatchError",
    "FailedHackError",
]

from typing import Any

from .raising import SstCoreError


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
