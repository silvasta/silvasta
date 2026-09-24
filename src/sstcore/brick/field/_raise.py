"""
Adapt the SstCoreError to the Fields and implement Raiser

- The Implementation

                                                 DependencyLevel[X]
"""

from enum import auto
from typing import Any, Never, Protocol, Unpack, cast

from ...port.raising import (
    ErrorDTO,
    ErrorInput,
    ErrorMachine,
    ErrorSpec,
    Raiser,
    SstCoreError,
)
from ..labor import clsname


class FieldErrorInput[FieldT, UnitT: Any](ErrorInput, total=False):
    """Define the Kwarg Space of the Error pipeline"""

    # TODO: make them as well args from here?
    # field: FieldT
    # instance: UnitT | None
    cls_attr_name: str
    #
    owner: type | None
    value: UnitT | Any
    #
    expected: dict
    received: dict


class FieldErrorSpec[FieldT, UnitT](ErrorSpec):
    """Define the Arg Space of the Internal Pipeline"""

    field: FieldT
    instance: UnitT | None = None
    cls_attr_name: str = ""  # "Cls.attr"

    owner: type | None = None
    value: FieldT | Any = None


class ErrorBuilder(ErrorMachine):
    def custom(self, reason: Raiser, **kwargs) -> type[SstCoreError]:
        """Get Custom Exception registred in Raiser"""
        return get_custom_exception(cast(FieldRaiser, reason))

    def builtin(self, reason: Raiser, **kwargs) -> type[Exception] | None:
        """Find Builtin Exception if registred in Raiser"""
        return get_builtin_exception(cast(FieldRaiser, reason))

    def message(self, reason: Raiser, **kwargs) -> str:
        """Find Builtin Exception if registred in Raiser"""
        return f"{reason}: {kwargs!r}"


class FieldRaiseCall(Protocol):
    def __call__(
        self,
        field: Any,
        instance: type | None = None,
        **kwargs: Unpack[ErrorInput],
    ) -> ErrorDTO: ...


class FieldRaiser(Raiser):
    RAW = auto()  # IDEA: this as index 0? (later)

    WriteExists = auto()
    ReadMissing = auto()
    ReadOnly = auto()
    Validation = auto()
    Function = auto()
    Signature = auto()
    Transition = auto()

    __call__: FieldRaiseCall

    def order(self, data: ErrorSpec) -> ErrorDTO:
        return ErrorBuilder.run(reason=self, data=data)

    def __str__(self):
        return self.name

    def map(self, name, field, value):
        # NEXT:
        # REFACTOR: complete split, fill the get_* matches
        match self:
            case FieldRaiser.WriteExists:
                f"{name}: {self} already Exists! {field}"
                AttributeError()
            case FieldRaiser.ReadMissing:
                f"{name}: {self} is Missing! {field}"
                AttributeError()
            case FieldRaiser.ReadOnly:
                # set by OnlyReadField or anything else
                reject = value
                f"{name}: {self} is not Writable! {reject=}"
                TypeError()
            case FieldRaiser.Validation:
                # bad input for function attach
                # IDEA: move this to FieldRaiser.Signature,
                # remove missing there and slots are filled
                signature = field
                bad_func = value
                f"{name}: expected {signature=}, got {bad_func=}"
                TypeError()
                # bad input for function execution
                types = value
                f"{name}: expected {types}, got {clsname(value)}"
                ValueError()
            case FieldRaiser.Function:
                bad_func = str(field)
                f"{name}: {self} is Missing! {bad_func=}"
                RuntimeError()
                f"Not Callable, {value=}! {self}"
                TypeError()
            case FieldRaiser.Signature:
                bad_func = str(field)
                f"{name}: {self} is Missing! {bad_func=}"
                RuntimeError()
            case FieldRaiser.Transition:
                states = str(field)  # CHECK:
                f"Failed transfer for {name}: {states}"
                RuntimeError()


def get_format_pattern(reason: FieldRaiser) -> str:
    match reason:
        case FieldRaiser.RAW:
            return ""
        case FieldRaiser.WriteExists:
            return ""
        case FieldRaiser.ReadMissing:
            return ""
        case FieldRaiser.ReadOnly:
            return ""
        case FieldRaiser.Validation:
            return ""
        case FieldRaiser.Function:
            return ""
        case FieldRaiser.Signature:
            return ""
        case FieldRaiser.Transition:
            return ""
    raise NotImplementedError(reason)


def get_builtin_exception(reason: FieldRaiser) -> type[Exception] | None:
    match reason:
        case FieldRaiser.RAW:
            return None
        case FieldRaiser.WriteExists:
            return None
        case FieldRaiser.ReadMissing:
            return None
        case FieldRaiser.ReadOnly:
            return None
        case FieldRaiser.Validation:
            return None
        case FieldRaiser.Function:
            return None
        case FieldRaiser.Signature:
            return None
        case FieldRaiser.Transition:
            return None
    raise NotImplementedError(reason)


def get_custom_exception(reason: FieldRaiser) -> type[SstCoreError]:
    match reason:
        case FieldRaiser.RAW:
            return SstCoreError
        case FieldRaiser.WriteExists:
            raise NotImplementedError
        case FieldRaiser.ReadMissing:
            raise NotImplementedError
        case FieldRaiser.ReadOnly:
            raise NotImplementedError
        case FieldRaiser.Validation:
            raise NotImplementedError
        case FieldRaiser.Function:
            raise NotImplementedError
        case FieldRaiser.Signature:
            raise NotImplementedError
        case FieldRaiser.Transition:
            raise NotImplementedError
    raise NotImplementedError(reason)


class FieldError(SstCoreError):
    # IDEA: use this FieldError and mix it with the errors above
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


#  LINE: -- USAGE -- -- - -- -- - -- -- - -- -- - -- -- - -- --

on_error = FieldRaiser
on_error.ReadOnly("blau", test=3)


def how_to_use1() -> Never:
    raise on_error.ReadMissing()()


def how_to_use0() -> ErrorDTO:
    return on_error.ReadMissing()()


def how_to_use2() -> ErrorDTO:
    return on_error.ReadMissing()


def how_to_use3() -> Never:
    assembled: ErrorDTO = on_error.ReadMissing(name="test")
    return assembled.fire()


def how_to_use4() -> Never:
    on_error.ReadMissing("", value="test")()
