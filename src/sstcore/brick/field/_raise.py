"""
Adapt the SstCoreError to the Fields and implement Raiser

- FieldRaiser(Raiser)
  - WriteExists = auto()
  - ReadMissing = auto()
  - ReadOnly = auto()
  - Validation = auto()
  - Function = auto()
  - Signature = auto()
  - Transition = auto()
    RAW = auto()

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "FieldError",
    "FieldErrorInput",
    "FieldErrorData",
    "FieldRaiseCall",
    "FieldRaiser",
]


from enum import auto
from typing import Any, Literal, NoReturn, Protocol, Unpack, overload

from ...port.raising import (
    ErrorData,
    ErrorDTO,
    ErrorInput,
    Raiser,
    SstCoreError,
)
from ..labor import clsname


class FieldError(SstCoreError):
    """Custom Exception for Field Operations"""

    def __init__(
        self,
        message: str,
        field: object,
        *args,
        panic: FieldRaiser | None = None,
        **kwargs: Any,
    ):
        self.message: str = message
        self.field: object = field
        self.kwargs: dict = kwargs
        self.panic: FieldRaiser = panic or FieldRaiser.RAW
        super().__init__(*args)


class FieldErrorInput[FieldT, UnitT: Any](ErrorInput, total=False):
    """Define the Kwarg Space of the Error pipeline"""

    attr: str
    owner: type | None
    value: UnitT | Any


class FieldErrorData[FieldT, UnitT](ErrorData):
    """Define the Arg Space of the Internal Pipeline"""

    field: FieldT | None = None
    instance: UnitT | None = None
    attr: str = ""
    owner: type | None = None
    value: FieldT | Any = None


class FieldRaiser(Raiser):  # TARGET: here is the most important part
    RAW = auto()

    WriteExists = auto()
    ReadMissing = auto()
    ReadOnly = auto()
    Validation = auto()
    Function = auto()
    Signature = auto()
    Transition = auto()

    __call__: FieldRaiseCall

    @property
    def data(self) -> type[FieldErrorData]:
        """Override to map to specific ErrorData"""
        return FieldErrorData

    @property
    def custom(self) -> type[SstCoreError]:
        """Override to map to specific Custom Error"""
        return FieldError

    @property
    def builtin(self) -> type[Exception] | None:
        """Override to map to builtin Exceptions"""
        match self:
            case FieldRaiser.RAW:
                return None

            case FieldRaiser.WriteExists:
                return AttributeError

            case FieldRaiser.ReadMissing:
                return AttributeError

            case FieldRaiser.ReadOnly:
                return TypeError

            case FieldRaiser.Validation:
                return ValueError

            case FieldRaiser.Function:
                return TypeError

            case FieldRaiser.Signature:
                return TypeError

            case FieldRaiser.Transition:
                return RuntimeError

    def message(self, data: ErrorData) -> str:
        """Override to generate formatted messages based on the Enum state"""

        assert isinstance(data, FieldErrorData), (
            f"Expected FieldErrorData, got {type(data)}"
        )
        name: str = data.attr or "Unknown"
        field: Any = data.field
        value: Any = data.value
        match self:
            case FieldRaiser.RAW:
                return super().message(data)

            case FieldRaiser.WriteExists:
                return f"{name}: {self.name} already Exists! {field}"

            case FieldRaiser.ReadMissing:
                return f"{name}: {self.name} is Missing! {field}"

            case FieldRaiser.ReadOnly:
                return f"{name}: {self.name} is not Writable! reject={value}"

            case FieldRaiser.Validation:
                return f"{name}: expected {value}, got {clsname(value) if value else 'None'}"

            case FieldRaiser.Function:
                return f"Not Callable, {value=}! {self.name}"

            case FieldRaiser.Signature:
                return f"{name}: expected {field=}, but got {value=}"

            case FieldRaiser.Transition:
                return f"Failed transfer for {name}: {field}"


class FieldRaiseCall(Protocol):
    @overload
    def __call__(
        self,
        field,
        instance,
        text: str = "",
        /,
        *args,
        mode: Literal["dto"],
        **kwargs: Unpack[FieldErrorInput],
    ) -> ErrorDTO: ...

    @overload
    def __call__(
        self,
        field,
        instance,
        text: str = "",
        /,
        *args,
        mode: Literal["exception"] = "exception",
        **kwargs: Unpack[FieldErrorInput],
    ) -> Exception: ...

    @overload
    def __call__(
        self,
        field,
        instance,
        text: str = "",
        /,
        *args,
        mode: Literal["raise"],
        **kwargs: Unpack[FieldErrorInput],
    ) -> NoReturn: ...

    def __call__(
        self,
        text: str = "",
        /,
        *args,
        mode: Literal["dto", "exception", "raise"] = "exception",
        **kwargs: Unpack[FieldErrorInput],
    ) -> ErrorDTO | Exception | NoReturn: ...
