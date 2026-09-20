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

from typing import Any, NamedTuple, Never, Protocol, TypedDict, Unpack

from .calling import Stringable
from .govern import EnumZero, Machine


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


class ErrorData[TargeT, UnitT](NamedTuple):
    """Define the Arg Space of the Internal Pipeline"""

    raiser: ErrorRaiser
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


class ErrorFormating[ErrorT: SstCoreError](Protocol):
    """Hold templates and fill values"""

    def template(self, reason: Raiser, /) -> str:
        """Store one template for each raising reason"""

    def format(self, keys: dict[str, Stringable]) -> str:
        """Insert keys and get filled pattern"""

    def __call__[TargeT](self, reason: Raiser, /, data: ErrorData) -> str:
        """Process Reason, Field and Data to"""


class ErrorProducing[ErrorT: SstCoreError](Protocol):
    """Order the Components, Build the Errors and provide DTOs"""

    def compose(self, reason: ErrorRaiser, /, data: ErrorData) -> ErrorT:
        """Mix builtin Exception into the custom Error"""

    def run(self, reason: ErrorRaiser, /, data: ErrorData) -> ErrorDTO:
        """Connect Raiser, Assemble and Format to build the Error"""

    def build(self, reason: ErrorRaiser, /, data: ErrorData) -> ErrorT: ...

    def __call__(
        self, reason: ErrorRaiser, /, data: ErrorData
    ) -> ErrorDTO[ErrorT]:
        """Collect Format and Compose Exception -> Build DTO"""


class ErrorMachine(Machine):
    """Start the Heavy Engine and Produce the Exceptions"""

    def sst_errors[ErrorT: SstCoreError](
        self, reason: Raiser, /, data: ErrorData
    ) -> ErrorDTO[ErrorT]:
        """Show all N SstCoreErrors"""
        raise NotImplementedError

    def exceptions(self, reason: ErrorRaiser, /, data: ErrorData) -> ErrorDTO:
        """Show all 0..N Builtin Exceptions"""
        raise NotImplementedError

    def build[ErrorT](self, reason: ErrorRaiser, /, data: ErrorData) -> ErrorT:
        raise NotImplementedError

    @classmethod
    def run[ErrorT: SstCoreError](
        cls, reason: ErrorRaiser, /, data: ErrorData
    ) -> ErrorDTO:
        raise NotImplementedError

    def __call__[ErrorT: SstCoreError](
        self, reason: ErrorRaiser, /, data: ErrorData
    ) -> ErrorDTO[ErrorT]:
        raise NotImplementedError


class ErrorRaiser(Protocol):
    def __call__(self, **kwargs: Unpack[ErrorInput]) -> Exception: ...
    def sanitize(**kwargs: Unpack[ErrorInput]) -> ErrorData: ...
    def launch(self, data: ErrorDTO, *args) -> Never: ...


class RaiserQuery[ErrorT: SstCoreError](Protocol):
    def __iter__(self) -> tuple[Single[ErrorT] | ErrorPair[ErrorT], ...]:
        """Yield all pairs of Error/Exception"""

    def __contains__(self, target: ErrorT | Exception) -> bool:
        """Is the target Exception already member?"""

    def errors(self) -> tuple[SstCoreError, ...]:
        """Provide all custom Errors, full mapping"""

    def exceptions(self) -> tuple[Exception, ...]:
        """Provide all builtin Exceptions, can be empty"""


class Raising[ErrorT: SstCoreError](RaiserQuery[ErrorT], Protocol):
    """Core"""

    # TASK: routing, input parsing TypedDict->NamedTuple

    def intact[TargeT, UnitT](
        self, field: TargeT, instance: UnitT, **kwargs: Unpack[ErrorInput]
    ) -> ErrorT: ...

    def __call__[TargeT, UnitT](
        self, field: TargeT, instance: UnitT, **kwargs: Unpack[ErrorInput]
    ) -> Never:
        """Take all relevant input, process, raise"""


class Raiser(EnumZero):
    def __call__(self, **kwargs: Unpack[ErrorInput]) -> Never:
        """Collect the needed input, format and fire the Exception"""

        # NEXT: catch and handler

        def _sanitize(**kwargs: Unpack[ErrorInput]) -> ErrorData:
            raise NotImplementedError

        input_dto: ErrorData = _sanitize(**kwargs)
        output_dto: ErrorDTO = ErrorMachine.run(self, data=input_dto)()

        self.launch(output_dto)

    def sanitize(**kwargs: Unpack[ErrorInput]) -> ErrorData:
        raise NotImplementedError

    def launch(self, data: ErrorDTO, *args) -> Never:
        raise data.fire(data.message, *data.args, *args)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class FailedHackError(SstCoreError):
    """
    It was a nice try, but...

    (I hope I don't have to  explain that this is mostly for internal tests...)
    """

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__("...I told you it will fail!", *args)
