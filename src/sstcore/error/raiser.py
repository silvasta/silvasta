"""
Assemble Setup with all Sst(Core)Errors

- provide heavy defaults
- create simple selection
- ensure easy modification

"""

__all__: list[str] = [
    "SstRaiserCall",
    "SstErrorInput",
    "SstErrorSpec",
    "SstRaiser",
]


# TODO: set imports private (or module)
from dataclasses import dataclass
from enum import auto
from typing import Any, Protocol, Unpack

from ..port.raising import (
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

# TASK: compare with all internal errors
# - build catalog plus handler here


class _SstError(SstError):
    """Finally Merge with SstError"""

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


class SstRaiserCall(Protocol):
    def __call__(self, *args, **kwargs: Unpack[SstErrorInput]) -> SstError:
        """Annotate the Raiser Input and Output"""


class SstErrorInput(ErrorInput, total=False): ...


@dataclass(frozen=True)
class SstErrorSpec(ErrorSpec): ...


class SstRaiser(Raiser):
    Zero = auto()

    Dispatch = auto()
    TuiSelect = auto()
    PathGuard = auto()
    Registry = auto()

    __call__: SstRaiserCall

    @property
    def spec(self) -> type[SstErrorSpec]:
        return SstErrorSpec

    @property
    def custom(self) -> type[SstError]:
        return SstError

    @property
    def builtin(self) -> type[Exception] | None:
        """Provide Builtin Exception if registered in Raiser"""
        match self:
            case SstRaiser.Zero:
                return SstError

            case SstRaiser.Dispatch:
                return NotImplementedDispatchError  # or logic error

            case SstRaiser.TuiSelect:
                # TODO: extend tui area, as well cli!
                return TuiSelectorError

            case SstRaiser.PathGuard:
                # IDEA: dispatch on PathGuardReason?
                return PathGuardError  # everything  possible...

            case SstRaiser.Registry:
                return RegistrySyncError

    def message(self, data: ErrorSpec) -> str:
        # NEXT: custom presets per error
        """Override to generate formatted messages based on the Enum state"""
        return f"Error in Sst!! ... {data.reason}"
