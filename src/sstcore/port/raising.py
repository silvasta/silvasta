"""
Provide Namespace for Exceptions before SstError is ready

- sstcore.error[L2] Avaliable for most of the Library
- sstcore.brick[L1] Build essential parts of the Errors
- sstcore. port[L0] Generally No Errors needed...

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "SstCoreError",
    "FailedHackError",
]

from dataclasses import dataclass
from typing import Any, Literal, NamedTuple, Never, NoReturn, TypedDict, Unpack

from .govern import EnumMachine, EnumZero


class SstCoreError(Exception):
    """Match and Catch all Errors on Global DependencyLevel[2]"""

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__(*args)

    def __repr__(self) -> str:
        """Show Everything"""
        _vars = [f"{k}={v!r}" for k, v in vars(self).items()]
        return f"{type(self).__name__}[{', '.join(_vars)}]"

    @classmethod
    def panic(cls, reason: EnumZero): ...


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

type ErrorPair[ErrorT] = SstCoreError | Exception
type Single[ErrorT] = SstCoreError | None


class ErrorInput(TypedDict, total=False):
    """Define the Kwarg Space of the Error Pipeline"""

    expected: dict
    received: dict


@dataclass(frozen=True)
class ErrorData:
    """Define the Arg Space of the Internal Pipeline"""

    reason: Raiser

    # IDEA: instead of dict and tuple reconstructing dict:
    # - use PortLinkData as template, create Edit/Static-Dict?
    # - combine expected/received,

    expected: tuple[tuple[str, Any], ...] = ()
    received: tuple[tuple[str, Any], ...] = ()

    extra: dict[str, Any] | None = None  # CHECK: can here something change?


class ErrorEntry(NamedTuple):  # IDEA: something like this?
    name: str
    value: Any
    cat: Literal["expected", "received", "extra"]
    info: str | None = None


@dataclass(frozen=True)
class ErrorDTO[ErrorT: Exception]:
    """Define the Boundary of the Outgoing Message"""

    error: type[ErrorT]
    message: str = ""
    args: tuple[Any, ...] = ()

    def __call__(self, *args) -> ErrorT:
        return self.error(self.message, *self.args, *args)

    def fire(self, *args) -> Never:
        raise self(*args)


type Errors = tuple[type[Exception], ...]


class ErrorMachine(EnumMachine):
    """Start the Heavy Engine and Produce the Exceptions"""

    @classmethod
    def custom(cls, data: ErrorData) -> type[SstCoreError]:
        """Get Custom Exception registred in Raiser"""
        return SstCoreError

    @classmethod
    def builtin(cls, data: ErrorData) -> type[Exception] | None:
        """Find Builtin Exception if registred in Raiser"""
        return Exception

    @classmethod
    def message(cls, data: ErrorData) -> str:
        """Find Builtin Exception if registred in Raiser"""
        return f"{data.reason}: ..."

    #  LINE: -- override the above methods -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    @classmethod
    def bases(cls, data: ErrorData) -> Errors:
        """Gather the registed Error classes"""
        sst_error: type[SstCoreError] = cls.custom(data)
        exception: type[Exception] | None = cls.builtin(data)
        return (sst_error,) if exception is None else (sst_error, exception)

    @classmethod
    def error_name(cls, reason: Raiser, bases: Errors) -> str:
        error: str = bases[-1].__name__
        prefix: str = bases[0].__name__[0:-5]  # CHECK: idea is, cut: Error
        return f"{reason.name}{prefix}{error}"

    @classmethod
    def compose(cls, data: ErrorData) -> type[SstCoreError]:
        """Mix builtin Exception into the custom Error"""
        bases: Errors = cls.bases(data)
        name: str = cls.error_name(data.reason, bases)
        return type(name, bases, {})

    @classmethod
    def run(cls, data: ErrorData) -> ErrorDTO:
        return ErrorDTO(
            error=cls.compose(data),
            message=cls.message(data),
        )


class Raiser(EnumZero):
    def __call__(
        self,
        message: str | None = None,
        /,
        *args,
        launch: bool = False,
        **kwargs: Unpack[ErrorInput],
    ) -> Exception | NoReturn:
        """Generate the DTO and immediately instantiate the Exception"""

        error_output: ErrorDTO = self.dto(*args, **kwargs)
        if launch:
            # FIX: args/message!! unite the pipeline, check with Data and DTO
            error_output.fire(*args)
        else:
            return error_output(message)

    def sanitize(self, *args, **kwargs: Unpack[ErrorInput]) -> ErrorData:
        """Extract the ErrorInput to form the ErrorData"""
        return ErrorData(self, *args, **kwargs)

    def order(self, data: ErrorData) -> ErrorDTO:
        """Produce the final ErrorDTO with the recipe in ErrorData"""
        return ErrorMachine.run(data)

    def dto(self, *args, **kwargs: Unpack[ErrorInput]) -> ErrorDTO:
        """Provide raw error output"""
        process_data: ErrorData = self.sanitize(*args, **kwargs)
        return self.order(process_data)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# MOVE: to ._error?
class FailedDispatchError(SstCoreError, NotImplementedError):
    # TASK: sync with NotImplementedDispatchError
    """Raise on missing TargetType for singledispatch(method)"""

    def __init__(self, first: Any, *args: Any, **kwargs):
        self.first = first
        msg = f"Missing dispatch target for {type(first).__name__}"
        super().__init__(msg, *(first, *args), **kwargs)


class FailedHackError(SstCoreError):
    """
    It was a nice try, but...

    (I hope I don't have to  explain that this is mostly for internal tests...)
    """

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__("...I told you it will fail!", *args)
