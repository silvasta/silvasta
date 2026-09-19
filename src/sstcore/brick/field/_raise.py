"""
Adapt the SstCoreError to the Fields and implement Raiser

- The Implementation

                                                 DependencyLevel[X]
"""

from enum import Enum, auto
from typing import Any, Never, Unpack

from ...port.attach import DescriptorBase
from ...port.raising import ErrorData, ErrorInput, SstCoreError
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
    cls_attr_name: str = ""  # Cls.attr
    #
    owner: type | None = None
    value: FieldT | Any = None


class FieldError(SstCoreError):
    # IDEA: use this FieldError and mix it with the errors above
    def __init__(
        self,
        message: str,
        field: object,
        *args,
        panic: FieldRaiser = FieldRaiser.RAW,
        **kwargs: Any,
    ):
        self.message: str = message
        self.field: object = field
        self.kwargs: dict = kwargs
        self.panic: FieldRaiser = panic
        super().__init__(*args)


class ErrorBuilder:
    def custom(
        self, reason: FieldRaiser, /, data: error.ErrorData
    ) -> error.ErrorDTO:
        """Get registred custom Exception that maps to current Raiser"""
        raise NotImplementedError

    def builtin(
        self, reason: FieldRaiser, /, data: error.ErrorData
    ) -> error.ErrorDTO:
        """Find registred builtin Exception if registred"""
        raise NotImplementedError

    def compose(
        self, reason: FieldRaiser, /, data: error.ErrorData
    ) -> type[SstCoreError]:
        """Mix builtin Exception into the custom Error"""

        def _name(data) -> str:
            # TODO:
            raise NotImplementedError

        sst_error = self.custom(reason, data)
        # FIX:
        exception = self.builtin(reason, data)
        bases: tuple[type[Exception], ...] = (
            # FIX:
            (sst_error, builtin)
            if (exception := self.builtin(reason, data))
            # FIX:
            else (sst_error := self.custom(reason, data))
        )

        new_cls: type = type(_name(data), bases, {})
        return new_cls

    def __call__(
        self, reason: error.Raiser, /, data: error.ErrorData
    ) -> error.ErrorDTO:
        """Mix builtin Exception into the custom Error"""
        raise NotImplementedError


class FieldRaiser(Enum):
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

    def __call__(self, **kwargs: Unpack[error.ErrorInput]) -> Never:
        """Collect the needed input, format and fire the Exception"""

        _field: DescriptorBase

        def _sanitize(**kwargs) -> error.ErrorInput:
            raise NotImplementedError

        input_dto: ErrorInput = _sanitize(**kwargs)
        output_dto: ErrorDTO = ErrorBuilder()(self, input_dto)

        self.launch(output_dto)

    def launch(self, data: error.ErrorDTO, *args) -> Never:
        raise data.fire(data.message, *data.args, *args)

    def map(self, name, field, value):
        # NEXT:
        # NEXT:
        # NEXT:
        # REFACTOR: complete split
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


# NOTE: grammar and text and everything for sure needs improvement
on_error = FieldRaiser

# IMPORTANT: finally that is executed in field
on_error.ReadMissing(object, name="test").raiser()


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
