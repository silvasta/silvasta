"""
Assemble Setup with all Sst(Core)Errors

- provide heavy defaults
- create simple selection
- ensure easy modification

"""

# IMPORTANT:
# STRATEGY: sstco

__all__: list[str] = [
    "SstRaiserCall",
    "SstErrorInput",
    "SstErrorData",
    "ErrorBuilder",
    "SstRaiser",
]


from dataclasses import dataclass
from enum import auto
from typing import Any, Protocol, Unpack

from ..port.raising import (
    ErrorData,
    ErrorDTO,
    ErrorInput,
    Raiser,
)
from ._base import SstError
from ._data import RegistrySyncError
from ._general import (
    NotImplementedDispatchError,
    TuiSelectorError,
)
from ._pathguard import PathGuardError


class SstRaiserCall(Protocol):
    def __call__(self, *args, **kwargs: Unpack[SstErrorInput]) -> SstError:
        """Annotate the Raiser Input and Output"""


class SstErrorInput(ErrorInput, total=False):
    text: str  # REMOVE: maybe to base or to *args,_input


@dataclass(frozen=True)
class SstErrorData(ErrorData):
    reason: SstRaiser
    text: str | None = None


_check: type[SstError] = NotImplementedDispatchError


class ErrorBuilder:
    # FIX: structure in builder is broken... split!
    # - EnumMachine for building
    # - Raiser for selecting, Or for Orchestration
    # - 1 non-enum part in the chain!!
    @classmethod
    def custom(cls, data: SstErrorData) -> type[SstError]:
        """Get Custom Exception registred in Raiser"""
        match data.reason:
            case SstRaiser.RAW:
                return SstError

            case SstRaiser.Dispatch:
                # TODO: check all internal errors, what is needed, how to provide best?
                return NotImplementedDispatchError  # or logic error

            case SstRaiser.TuiSelector:
                # TODO: extend tui area, as well cli!
                return TuiSelectorError

            case SstRaiser.PathGuard:
                # IDEA: dispatch on PathGuardReason?
                return PathGuardError  # everything  possible...

            case SstRaiser.Registry:
                return RegistrySyncError

    @classmethod
    def builtin(cls, data: ErrorData) -> type[Exception] | None:
        """Find Builtin Exception if registred in Raiser"""
        match data.reason:
            case SstRaiser.RAW:
                ...
            case SstRaiser.Dispatch:
                # TODO: check all internal errors, what is needed, how to provide best?
                # return RuntimeError  # or logic error
                ...  # already has NotImplementedError

            case SstRaiser.TuiSelector:
                # TODO: extend tui area, as well cli!
                return RuntimeError

            case SstRaiser.PathGuard:
                # IDEA: dispatch on PathGuardReason?
                return OSError  # everything  possible...

            case SstRaiser.Registry:
                return ValueError  # everything  possible...

    @classmethod
    def message(cls, data: ErrorData) -> str:
        """Find Builtin Exception if registred in Raiser"""
        # TODO:
        return f"Error in Sst!! ... {data.reason}"


class SstRaiser(Raiser):
    RAW = auto()

    Dispatch = auto()
    TuiSelector = auto()
    PathGuard = auto()
    Registry = auto()

    __call__: SstRaiserCall

    def order(self, data: ErrorData) -> ErrorDTO:
        return ErrorBuilder.run(data)


class SstError(SstError):
    def __init__(
        self,
        message: str,
        *args,
        text: str | None = None,
        panic: SstRaiser | None = None,
        **kwargs: Any,
    ):
        self.message: str = message
        self.doc_text: str | None = text
        self.kwargs: dict = kwargs
        self.panic: SstRaiser = panic or SstRaiser.RAW
        super().__init__(*args)
