"""
Adapt the SstError to PortLink

- This is intends as the one and only Raiser Implementation in the port
- Still experimental, like the setups outside the port

                                  DependencyLevel.sstcore.port[0.X]
"""

__all__: list[str] = [
    "SstError",
    "SstPortError",
    #
    "mix_error",
    "rebuild",
    #
    "FailedDispatchError",
    "FailedHackError",
]

from functools import cache
from typing import Any

from ._types import Types as _T  # noqa:N814
from .structures._primitives import Kwargs


class SstError(Exception):
    """The Root of all sst Exceptions"""

    def __init__(self, *args, **kwargs) -> None:
        """Forward Args to Exception and Flatten Kwargs"""
        # AI: that was one of the reasons for the initial kwargs idea
        super().__init__(*args, *Kwargs(kwargs).args())

    @property
    def name(self) -> str:
        return type(self).__name__

    def __old__repr__(self) -> str:
        _vars = (f"{k}={v!r}" for k, v in vars(self).items())
        return f"{self.name}[{', '.join(_vars)}]"

    def __repr__(self) -> str:
        # AI: this is the second slightly improvement
        return f"{self.name}[{Kwargs.vars(self)}]"


class SstPortError(SstError):
    """Match and Catch all Errors in the lowest Port Layers"""


#  LINE: -- Dynamic Features -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@cache
def mix_error(name: str, bases: _T.Errors, module: str = "") -> type[SstError]:
    """Dynamically create and cache a picklable Exception class"""

    def _reduce(self: Exception) -> tuple[Any, ...]:
        return (rebuild, (name, bases, module, self.args))

    namespace = {
        "__module__": module or __name__,
        "__qualname__": name,
        "__reduce__": _reduce,
    }
    return type(name, bases, namespace)


def rebuild(name: str, bases: _T.Errors, module: str, args: tuple) -> SstError:
    """Top-level pickle hook to rebuild a dynamically mixed exception"""
    error_cls = mix_error(name, bases, module)
    return error_cls(*args)


# AI: the version above looks better, 1 line more, therefore way  cleaner
def _rebuild(name: str, bases: _T.Errors, module: str, args: tuple) -> SstError:
    """Top-level pickle hook to rebuild a dynamically mixed exception"""
    return mix_error(name, bases, module)(*args)


#  LINE: -- Implementations -- -- - -- -- - -- -- - -- -- - -- -- - -- --


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
