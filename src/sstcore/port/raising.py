"""
Provide Namespace for Exceptions before SstError is ready

- sstcore.error[L2] Avaliable for most of the Library
- sstcore.brick[L1] Build essential parts of the Errors
- sstcore. port[L0] Generally No Errors needed...

                                    DependencyLevel.sstcore.port[2]

"""

__all__: list[str] = [
    "SstCoreError",
    "ErrorDTO",
    "ErrorInput",
    "ErrorData",
    "Raiser",
]

from dataclasses import dataclass
from typing import (
    Any,
    Literal,
    Never,
    NoReturn,
    Self,
    TypedDict,
    Unpack,
    overload,
)

from .solid import BaseEnum

type Errors = tuple[type[Exception]] | tuple[type[Exception], type[Exception]]


class SstCoreError(Exception):
    """Match and Catch all Errors on Global DependencyLevel[2]"""

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__(*args)

    @property
    def name(self) -> str:
        return type(self).__name__

    def __repr__(self) -> str:
        """Show Everything"""
        _vars = [f"{k}={v!r}" for k, v in vars(self).items()]
        return f"{type(self).__name__}[{', '.join(_vars)}]"

    @classmethod  # STRATEGY: do this latest in SstError!
    def panic(cls, reason: Raiser): ...


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


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


class ErrorInput(TypedDict, total=False):
    """Define the Kwarg Space of the Error Pipeline"""

    expected: dict
    received: dict


@dataclass(frozen=True)
class ErrorData:
    """Define the Arg Space of the Internal Pipeline"""

    reason: Raiser

    expected: dict[str, Any] | None = None
    received: dict[str, Any] | None = None

    extra: dict[str, Any] | None = None  # CHECK: can here something change?

    def __str__(self):
        return f"{type(self).__name__}[{self.reason}]"

    def __repr__(self):
        log: str = "-|-".join(f"{k}:={v}" for k, v in vars(self).items())
        return f"{self}({log})"

    @classmethod
    def absorb(
        cls, reason: Raiser, /, *args, **kwargs: Unpack[ErrorInput]
    ) -> Self:
        """Extract the ErrorInput kwargs to form the ErrorData"""

        items: dict[str, Any] = {}
        extra: dict[str, Any] = {}
        if args:
            extra["args"] = args

        _valid_fields = cls.__dataclass_fields__.keys()

        for key, value in kwargs.items():
            if key in _valid_fields:
                items[key] = value
            else:
                extra[key] = value

        return cls(reason, extra=extra, **items)


class Raiser(BaseEnum):
    """Assemble all data and throw it with panic"""

    @property
    def data(self) -> type[ErrorData]:
        return ErrorData

    @property
    def custom(self) -> type[SstCoreError]:
        return SstCoreError

    @property
    def builtin(self) -> type[Exception] | None:
        return Exception

    @property
    def error_name(self) -> str:
        match len(bases := self.bases):
            case 1:
                front = f"{bases[0].__name__}"
            case 2:
                front = f"{bases[0].__name__[0:-5]}{bases[-1].__name__}"
        return f"{self.name}{front}"

    def message(self, data: ErrorData) -> str:
        """Find Builtin Exception if registred in Raiser"""
        return repr(data)

    @property
    def bases(self) -> Errors:
        """Gather the registed Error classes"""
        sst_error: type[SstCoreError] = self.custom
        exception: type[Exception] | None = self.builtin
        # NOTE: Assuming data has no influence on selection
        return (sst_error,) if exception is None else (sst_error, exception)

    def compose(self) -> type[SstCoreError]:
        """Mix builtin Exception into the custom Error"""
        bases: Errors = self.bases
        name: str = self.error_name
        return type(name, bases, {})

    @overload
    def __call__(
        self,
        text: str = "",
        /,
        *args,
        mode: Literal["dto"],
        **kwargs: Unpack[ErrorInput],
    ) -> ErrorDTO: ...

    @overload
    def __call__(
        self,
        text: str = "",
        /,
        *args,
        mode: Literal["exception"] = "exception",
        **kwargs: Unpack[ErrorInput],
    ) -> Exception: ...

    @overload
    def __call__(
        self,
        text: str = "",
        /,
        *args,
        mode: Literal["raise"],
        **kwargs: Unpack[ErrorInput],
    ) -> NoReturn: ...

    def __call__(
        self,
        text="",
        /,
        *args,
        mode: Literal["dto", "exception", "raise"] = "exception",
        **kwargs: Unpack[ErrorInput],
    ) -> ErrorDTO | Exception | NoReturn:
        """Generate the DTO and immediately instantiate the Exception"""

        data: ErrorData = self.data.absorb(self, *args, **kwargs)
        error: type[SstCoreError] = self.compose()
        message: str = f"{self.message(data)} {text}".strip()
        _dto = ErrorDTO(error, message=message, args=args)

        match mode:
            case "dto":
                return _dto
            case "exception":
                return _dto(*args)
            case "raise":
                return _dto.fire(*args)
