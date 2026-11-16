"""
Adapt the SstError to PortLink

- This is intends as the one and only Raiser Implementation in the port
- Still experimental, like the setups outside the port

                                  DependencyLevel.sstcore.port[0.X]
"""

__all__: list[str] = [
    "SstError",
    "SstPortError",
    "FailedDispatchError",
    "FailedHackError",
]

from typing import Any


class SstError(Exception):
    """The Root of all sst Exceptions"""

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__(*args)

    @property
    def name(self) -> str:
        return type(self).__name__

    def __repr__(self) -> str:
        _vars = (f"{k}={v!r}" for k, v in vars(self).items())
        return f"{self.name}[{', '.join(_vars)}]"


class SstPortError(SstError):
    """Match and Catch all Errors in the lowest Port Layers"""


class FailedDispatchError(SstError, NotImplementedError):
    # TASK: sync with NotImplementedDispatchError
    """Raise on missing TargetType for singledispatch(method)"""

    def __init__(self, first: Any, *args: Any, **kwargs):
        self.first = first
        msg = f"Missing dispatch target for {type(first).__name__}"
        super().__init__(msg, *(first, *args), **kwargs)


class FailedHackError(SstError):
    """
    It was a nice try, but...

    (I hope I don't have to  explain that this is mostly for internal tests...)
    """

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__("...I told you it will fail!", *args)
