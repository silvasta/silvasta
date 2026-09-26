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

from typing import Any, NamedTuple, Never, TypedDict, Unpack

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


class ErrorSpec[TargeT, UnitT](NamedTuple):
    """Define the Arg Space of the Internal Pipeline"""

    raiser: Raiser
    #
    expected: tuple[tuple[str, Any], ...] = ()
    received: tuple[tuple[str, Any], ...] = ()
    #
    extra: dict[str, Any] | None = None  # CHECK: can here something change?


class ErrorDTO[ErrorT: Exception](NamedTuple):
    """Define the Boundary of the Outgoing Message"""

    error: type[ErrorT]
    message: str = ""
    args: tuple[Any, ...] = ()

    def __call__(self, *args) -> ErrorT:
        return self.error(self.message, *self.args, *args)

    def fire(self, *args) -> Never:
        raise self(self.message, *self.args, *args)


type Errors = tuple[type[Exception], ...]


class ErrorEnumMachine(EnumMachine):
    """Start the Heavy Engine and Produce the Exceptions"""

    def message(self, reason: Raiser, **kwargs) -> str:
        """Find Builtin Exception if registred in Raiser"""
        return f"{reason}: {kwargs!r}"

    def custom(self, reason: Raiser, **kwargs) -> type[SstCoreError]:
        """Get Custom Exception registred in Raiser"""
        return SstCoreError

    def builtin(self, reason: Raiser, **kwargs) -> type[Exception] | None:
        """Find Builtin Exception if registred in Raiser"""
        return Exception

    #  LINE: -- override the above methods -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def bases(self, reason: Raiser, **kwargs) -> Errors:
        """Gather the registed Error classes"""
        sst_error: type[SstCoreError] = self.custom(reason, **kwargs)
        exception: type[Exception] | None = self.builtin(reason, **kwargs)
        return (sst_error,) if exception is None else (sst_error, exception)

    def error_name(self, reason: Raiser, bases: Errors) -> str:
        error: str = bases[-1].__name__
        prefix: str = bases[0].__name__[0:-5]  # CHECK: idea is, cut: Error
        return f"{reason.name}{prefix}{error}"

    def compose(self, reason: Raiser, **kwargs) -> type[SstCoreError]:
        """Mix builtin Exception into the custom Error"""
        bases: Errors = self.bases(reason, **kwargs)
        name: str = self.error_name(reason, bases)
        return type(name, bases, {})

    @staticmethod
    def run(reason: Raiser, **kwargs) -> ErrorDTO:
        return ErrorDTO(
            error=ErrorEnumMachine.compose(reason=reason, **kwargs),
            message=ErrorEnumMachine.message(reason=reason, **kwargs),
        )


class Raiser(EnumZero):
    def __call__(self, *args, **kwargs: Unpack[ErrorInput]) -> ErrorDTO:
        """Collect the needed input, format and fire the Exception"""

        input_dto: ErrorSpec = self.sanitize(*args, **kwargs)
        output_dto: ErrorDTO = self.order(input_dto)

        return output_dto

    def launch(self, data: ErrorDTO, *args) -> Never:
        raise data.fire(data.message, *data.args, *args)

    def order(self, data: ErrorSpec) -> ErrorDTO:
        return ErrorEnumMachine.run(reason=self, data=data)

    def sanitize(self, *args, **kwargs) -> ErrorSpec:
        return ErrorSpec(self, *args, **kwargs)


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
