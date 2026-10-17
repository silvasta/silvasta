"""
Assemble Setup with all Sst(Core)Errors

- provide heavy defaults
- create simple selection
- ensure easy modification

"""

# IMPORTANT: outdatet, rebuild!

__all__: list[str] = [
    "SstRaiserCall",
    "SstErrorInput",
    "SstErrorSpec",
    "ErrorBuilder",
    "SstRaiser",
]


from dataclasses import dataclass
from enum import auto
from typing import Any, Protocol, Unpack

from ..port.raising import (
    ErrorDTO,
    ErrorInput,
    ErrorSpec,
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
class SstErrorSpec(ErrorSpec):
    reason: SstRaiser
    text: str | None = None


_check: type[SstError] = NotImplementedDispatchError


class ErrorBuilder:
    # FIX: structure in builder is broken... split!
    # - EnumMachine for building
    # - Raiser for selecting, Or for Orchestration
    # - 1 non-enum part in the chain!!
    @classmethod
    def custom(cls, data: SstErrorSpec) -> type[SstError]:
        """Get Custom Exception registered in Raiser"""
        match data.reason:
            case SstRaiser.Zero:
                return SstError

            case SstRaiser.Dispatch:
                # TODO: check all internal errors:
                # what is needed, how to provide best?
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
    def builtin(cls, data: ErrorSpec) -> type[Exception] | None:
        """Find Builtin Exception if registered in Raiser"""
        match data.reason:
            case SstRaiser.Zero:
                ...
            case SstRaiser.Dispatch:
                # TODO: check all internal errors:
                # what is needed, how to provide best?
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
    def message(cls, data: ErrorSpec) -> str:
        """Find Builtin Exception if registered in Raiser"""
        # TODO:
        return f"Error in Sst!! ... {data.reason}"


class SstRaiser(Raiser):
    Zero = auto()

    Dispatch = auto()
    TuiSelector = auto()
    PathGuard = auto()
    Registry = auto()

    __call__: SstRaiserCall

    def order(self, data: ErrorSpec) -> ErrorDTO:
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
        self.panic: SstRaiser = panic or SstRaiser.Zero
        super().__init__(*args)
