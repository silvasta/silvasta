"""
Adapt the SstCoreError to the Fields and implement Raiser

- class FieldRaiser(Raiser, zero=True)
    0 Zero = auto()
    1 WriteExists = auto()
    2 ReadMissing = auto()
    3 ReadOnly = auto()
    4 Validation = auto()
    5 Function = auto()
    6 Signature = auto()
    7 Transition = auto()

                                                 DependencyLevel[0]
"""

from dataclasses import dataclass

__all__: list[str] = [
    "FieldError",
    "FieldErrorInput",
    "FieldErrorSpec",
    "FieldRaiseCall",
    "FieldRaiser",
]


from enum import auto
from typing import Any, Literal, NoReturn, Protocol, Unpack, overload

from ...brick.none._sentinel import UNSET
from ...port import raising
from ...port.attach import Descriptor
from ...port.raising import Raiser
from ..reflect import clsname


class FieldError[FieldT: Descriptor](raising.SstCoreError):
    """Custom Exception for Field Operations"""

    def __init__(
        self,
        message: str,
        # AI: here it makes sense to avoid erasure of parametrized type
        field: FieldT | UNSET = UNSET,
        *args,
        # AI: for the enum below it just doesn't help in the best case
        panic: FieldRaiser | None = None,
        **kwargs: Any,
    ):
        self.message: str = message
        self.field: FieldT | UNSET = field
        self.kwargs: dict = kwargs
        self.panic: FieldRaiser = panic or FieldRaiser.Zero
        super().__init__(*args)


class FieldErrorInput[FieldT, UnitT: Any](raising.ErrorInput, total=False):
    """Define the Kwarg Space of the Error pipeline"""

    attr: str  # REMOVE: ?? this is basically field.public_name
    owner: type | None
    value: UnitT | Any


@dataclass(frozen=True, kw_only=True)
class FieldErrorSpec[FieldT, UnitT](raising.ErrorSpec):
    """Define the Arg Space of the Internal Pipeline"""

    # AI: in the dto it feels safe enough without
    # - i mean when i start at one, why not the others?
    # - finally using it for everything was not the point
    # explain how to handle this, before it overboards
    field: FieldT | None = None
    instance: UnitT | None = None
    attr: str = ""  # REMOVE: ?? this is basically field.public_name
    owner: type | None = None
    value: FieldT | Any = None


class FieldRaiser(Raiser, zero=True):
    Zero = auto()

    WriteExists = auto()
    ReadMissing = auto()
    ReadOnly = auto()
    Validation = auto()
    Function = auto()
    Signature = auto()
    Transition = auto()

    __call__: FieldRaiseCall

    @property
    def data(self) -> type[FieldErrorSpec]:
        """Override to map to specific raising.ErrorSpec"""
        return FieldErrorSpec

    @property
    def custom(self) -> type[FieldError]:
        """Override to map to specific Custom Error"""
        return FieldError

    @property
    def builtin(self) -> type[Exception] | None:
        """Override to map to builtin Exceptions"""
        match self:
            case FieldRaiser.Zero:
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

    def message(self, data: raising.ErrorSpec) -> str:
        """Override to generate formatted messages based on the Enum state"""

        assert isinstance(data, FieldErrorSpec), (
            f"Expected Fieldraising.ErrorSpec, got {type(data)}"
        )
        name: str = data.attr or "Unknown"
        field: Any = data.field
        value: Any = data.value

        match self:
            case FieldRaiser.Zero:
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

        return f"Issue with match in Self.message: {self=}"


class FieldRaiseCall(Protocol):  # LATER: think about parametrization
    # AI: here is actually the most difficult point:
    # - first: why is it needed or not
    # - second: how to do it proper in the overload?
    # - Third: killer criterium, how to actually get a real Field into the parametrization?
    #   - beside the less precise port Descriptors here probably better suited:
    #     - BaseField(NamedField): with attrs like default|frozen
    #     - NamedField: with public_name/private_name/name
    #   - when the dependency issue can be resolved and the parametrization is useful:
    #     - extend Descriptor protocol by the desired params
    #     - Read/Write makes no sense, type is narrowed inside but widened outside
    #       - meaning a field that has no 100% match can either not enter properly or not operate inside without warnings

    # AI_TASK: briefly analyze if the effort is worth the result

    @overload
    def __call__(
        self,
        field,
        instance: Any,  # LATER: senti?
        /,
        text: str = "",
        *args,
        mode: Literal["dto"],
        **kwargs: Unpack[FieldErrorInput],
    ) -> raising.ErrorDTO: ...

    @overload
    def __call__(
        self,
        field,
        instance: Any,  # LATER: senti?
        /,
        text: str = "",
        *args,
        mode: Literal["exception"] = "exception",
        **kwargs: Unpack[FieldErrorInput],
    ) -> Exception: ...

    @overload
    def __call__(
        self,
        field,
        instance: Any,  # LATER: senti?
        /,
        text: str = "",
        *args,
        mode: Literal["raise"],
        **kwargs: Unpack[FieldErrorInput],
    ) -> NoReturn: ...

    def __call__(
        self,
        text: str = "",
        *args,
        mode: Literal["dto", "exception", "raise"] = "exception",
        **kwargs: Unpack[FieldErrorInput],
    ) -> raising.ErrorDTO | Exception | NoReturn: ...
