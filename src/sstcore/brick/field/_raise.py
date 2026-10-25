"""
Adapt the SstCoreError to the Fields and implement Raiser

- class FieldRaiser(Raiser, zero=True)
    0 Zero        => SstCoreError default setup
    1 WriteExists => todo
    2 ReadMissing =>
    3 ReadOnly    =>
    4 Validation  =>
    5 Function    =>
    6 Signature   =>
    7 Transition  =>

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "FieldError",
    "FieldErrorInput",
    "FieldErrorSpec",
    "FieldRaiseCall",
    "FieldRaiser",
]


from dataclasses import dataclass
from enum import auto
from typing import Any, Protocol, Unpack

from ...port import raising
from ...port.attach import Descriptor
from ...port.empty import VOID, MayBe
from ...port.raising import Raiser
from ..reflect import clsname


class FieldError(raising.SstCoreError):
    """Custom Exception for Field Operations"""

    def __init__(
        self,
        message: str,
        field: Descriptor | None = None,
        *args,
        panic: MayBe[FieldRaiser] = VOID,
        **kwargs: Unpack[FieldErrorInput],
    ):
        self.message: str = message
        self.field: Descriptor | None = field
        self.kwargs: FieldErrorInput = kwargs
        self.panic: MayBe[FieldRaiser] = panic
        super().__init__(message, *args)


class FieldErrorInput[UnitT: Any](raising.ErrorInput, total=False):
    """Define the Kwarg Space of the Error pipeline"""

    owner: type | None
    value: UnitT | VOID


@dataclass(frozen=True, kw_only=True)
class FieldErrorSpec[UnitT](raising.ErrorSpec):
    """Define the Arg Space of the Internal Pipeline"""

    __pos_fields__ = ("field", "unit")

    field: Descriptor | None = None
    unit: UnitT | VOID = VOID
    owner: type | None = None
    value: Any | VOID = VOID

    def attr(self) -> Any | None:
        return None if self.field is None else self.field.public_name

    def __str__(self) -> str:
        """Find best Combination of available Nameable parts"""
        if self.field is not None:
            if self.unit is not VOID:
                return self.field.name(self.unit)
            if self.owner is not None:
                return self.field.name(self.owner)
            return f"{self.field}"
        if self.unit is not VOID:
            return f"{type(self.unit).__name__}[{self.unit}]"
        if self.owner is not None:
            return f"{self.owner.__name__}[...]"
        return f"{type(self).__name__}::UnNamed"


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class FieldRaiseCall(Protocol):
    def __call__(
        self,
        field: Descriptor | None = None,
        unit: Any | VOID = VOID,
        /,
        *args: Any,
        **kwargs: Unpack[FieldErrorInput],
    ) -> FieldError: ...


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
    def spec(self) -> type[FieldErrorSpec]:
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
        field: Descriptor | None = data.field
        value: Any | VOID = data.value

        match self:
            case FieldRaiser.Zero:
                return super().message(data)

            case FieldRaiser.WriteExists:
                return f"{data}: {self.name} already Exists! ({field})"

            case FieldRaiser.ReadMissing:
                return f"{data}: {self.name} is Missing! ({field})"

            case FieldRaiser.ReadOnly:
                return f"{data}: {self.name} is not Writable! rejected={value}"

            case FieldRaiser.Validation:  # TODO: this, and all others
                received: str = "VOID" if value is VOID else clsname(value)
                return f"{data}: expected {value=}, got {received=}"

            case FieldRaiser.Function:
                return f"Not Callable, {value=}! {self.name}"

            case FieldRaiser.Signature:
                # TODO:
                return f"{data}: {field=}, but got {value=}"

            case FieldRaiser.Transition:
                return f"Failed transfer for {data}: {field}"

        return f"Issue with match in Self.message: {self=}"
