"""
Adapt the SstCoreError to the Fields and implement Raiser

- The Implementation

                                                 DependencyLevel[X]
"""

import re

from enum import auto
from typing import Any, Literal, Never, Unpack, overload

from ...port.raising import (
    ErrorData,
    ErrorDTO,
    ErrorInput,
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


class FieldErrorData[FieldT, UnitT](ErrorData):
    """Define the Arg Space of the Internal Pipeline"""

    field: FieldT
    instance: UnitT | None = None
    cls_attr_name: str = ""  # "Cls.attr"
    #
    owner: type | None = None
    value: FieldT | Any = None


class ErrorBuilder:
    # EXTRACT: generic/field_specific
    def custom(
        self, reason: FieldRaiser, /, data: ErrorData
    ) -> type[SstCoreError]:
        """Get Custom Exception registred in Raiser"""
        raise NotImplementedError(reason, data)

    # EXTRACT: generic/field_specific
    def builtin(
        self, reason: FieldRaiser, /, data: ErrorData
    ) -> type[Exception] | None:
        """Find Builtin Exception if registred in Raiser"""
        raise NotImplementedError(reason, data)

    # EXTRACT: generic/field_specific
    def bases(
        self, reason: FieldRaiser, /, data: ErrorData
    ) -> tuple[type[Exception], ...]:
        """Gather the registed Error classes"""
        sst_error: type[SstCoreError] = self.custom(reason, data)
        exception: type[Exception] | None = self.builtin(reason, data)
        return (sst_error,) if exception is None else (sst_error, exception)

    # EXTRACT: generic/field_specific
    def error_name(
        self, reason: FieldRaiser, bases: tuple[type[Exception], ...]
    ) -> str:  # TODO: try less hardcoded
        """Format new Error class name"""
        error: str = bases[-1].__name__
        prefix: str = bases[0].__name__.rstrip("Error")  # FIX:
        return f"{reason.name}{prefix}{error}"  # CHECK: output

    # EXTRACT: generic/field_specific
    def compose(
        self, reason: FieldRaiser, /, data: ErrorData
    ) -> type[SstCoreError]:
        """Mix builtin Exception into the custom Error"""

        bases: tuple[type[Exception], ...] = self.bases(reason, data)
        name: str = self.error_name(reason, bases)

        return type(name, bases, {})

    # EXTRACT: generic/field_specific
    def __call__(self, reason: Raiser, /, data: ErrorData) -> ErrorDTO:
        """Mix builtin Exception into the custom Error"""
        raise NotImplementedError(reason, data)


class FieldRaiser(Raiser):
    RAW = auto()  # IDEA: this as index 0? (later)

    WriteExists = auto()
    ReadMissing = auto()
    ReadOnly = auto()
    Validation = auto()
    Function = auto()
    Signature = auto()
    Transition = auto()

    def __str__(self):
        return self.name

    @overload  # EXTRACT: generic/field_specific
    def __call__(
        self, direct=Literal[True], **kwargs: Unpack[ErrorInput]
    ) -> Never: ...
    @overload  # EXTRACT: generic/field_specific
    def __call__(
        self, direct=Literal[False], **kwargs: Unpack[ErrorInput]
    ) -> ErrorDTO: ...
    def __call__(  # EXTRACT: generic/field_specific
        self, direct: bool = False, **kwargs: Unpack[ErrorInput]
    ) -> Never | ErrorDTO:
        """Collect the needed input, format and fire the Exception"""

        # EXTRACT: generic/field_specific
        def _sanitize(**kwargs: Unpack[ErrorInput]) -> ErrorData:
            raise NotImplementedError(kwargs)

        input_data: ErrorData = _sanitize(**kwargs)
        error_dto: ErrorDTO = ErrorBuilder()(self, input_data)

        return error_dto if not direct else self.launch(error_dto)

    def launch(self, data: ErrorDTO, *args) -> Never:
        raise data.fire(data.message, *data.args, *args)

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


def how_to_use1() -> Never:
    raise on_error.ReadMissing(name="test", direct=False)


def how_to_use2() -> ErrorDTO:
    return on_error.ReadMissing(direct=False)


def how_to_use3() -> Never:
    assembled: ErrorDTO = on_error.ReadMissing(name="test")
    return assembled.fire()


def how_to_use4() -> Never:
    on_error.ReadMissing(name="test", direct=True)
