"""
Specify SstCoreError before SstError is ready

- sstcore.error[L2] Available for most of the Library
- sstcore.brick[L1] Build essential parts of the Errors
- sstcore. port[L0] Generally No Errors needed, but...
  - port._raise contains LinkRaiser for port.link, open for others

                                  DependencyLevel.sstcore.port[0.3]

"""

# IDEA: absorb _error and _raise

__all__: list[str] = [
    "SstCoreError",
    #
    "ErrorDTO",
    "ErrorInput",
    "ErrorSpec",
    "Raiser",
]

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Never, Self, TypedDict, Unpack

from .solid import BaseEnum
from .structures import ParamSpec

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
        _vars = [f"{k}={v!r}" for k, v in vars(self).items()]
        return f"{type(self).__name__}[{', '.join(_vars)}]"

    @classmethod  # STRATEGY: do this latest in sstcore.error.SstError!
    def panic(cls, reason: Raiser): ...


#  LINE: -- DTO, Input and Spec -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True)
class ErrorDTO:
    """Define the Boundary of the Outgoing Message"""

    error: type[SstCoreError]
    message: str = ""
    args: tuple[Any, ...] = ()

    def __call__(self, *args) -> SstCoreError:
        # CHECK: wired pipeline Raiser->DTO->Error proper!?
        return self.error(self.message, *self.args, *args)

    def fire(self, *args) -> Never:
        raise self(*args)


class ErrorInput(TypedDict, total=False):
    # LATER: create better pairs, improve:
    # - expected={"policy": PolicyEnum},
    # - received={"policy": policy},
    #   -> only 1 key for 2 values needed, avoid duplication and mismatches!
    # - Build some kind of ErrorComparisonRegistry that accepts[ManyInput]
    """Define the Kwarg Space of the Error Pipeline"""

    text: str
    expected: Mapping
    received: Mapping


class ErrorSpec(ParamSpec, frozen=True):
    """Define the Arg Space of the Internal Pipeline"""

    reason: Raiser
    text: str = ""
    expected: dict[str, Any] | None = None
    received: dict[str, Any] | None = None

    extra: dict[str, Any] | None = None  # CHECK: can here something change?

    __pos_fields__: tuple[str, ...] = ()

    def __str__(self):
        return f"{type(self).__name__}[{self.reason}]"

    @classmethod
    def capture(
        cls, reason: Raiser, /, *args, **kwargs: Unpack[ErrorInput]
    ) -> Self:
        """Extract the ErrorInput kwargs to form the ErrorSpec"""

        _items = dict(zip(cls.__pos_fields__, args, strict=False))
        _items.update(cls.field_names().pluck(kwargs, destroy=True))
        _extra = dict(kwargs)

        if len(args) > (n_positionals := len(cls.__pos_fields__)):
            _extra["args"] = args[n_positionals:]

        return cls(reason=reason, extra=_extra or None, **_items)


#  LINE: -- Raise -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Raiser(BaseEnum, zero=True, walk=True):
    """Assemble all data and throw it with panic"""

    def __call__(
        self, *args: Any, **kwargs: Unpack[ErrorInput]
    ) -> SstCoreError:
        """Generate the DTO and instantiate the Exception"""
        return self.dto(*args, **kwargs)()

    def fire(self, *args: Any, **kwargs: Unpack[ErrorInput]) -> Never:
        """Generate the DTO, assemble and directly throw the Exception"""
        self.dto(*args, **kwargs).fire()

    def dto(self, *args: Any, **kwargs: Unpack[ErrorInput]) -> ErrorDTO:
        """Sanitize the Input, compose Error and Message and create the DTO"""
        data: ErrorSpec = self.spec.capture(self, *args, **kwargs)
        error: type[SstCoreError] = self.compose()
        message: str = f"{self.message(data)} {data.text}".strip()
        return ErrorDTO(error, message=message, args=args)

    @property
    def spec(self) -> type[ErrorSpec]:
        """Keep and Provide the internal Error Data Specification"""
        return ErrorSpec

    @property
    def custom(self) -> type[SstCoreError]:
        """Provide the custom Error defined for Topic and Raiser"""
        return SstCoreError

    @property
    def builtin(self) -> type[Exception] | None:
        """Provide the builtin Error related to active Raiser"""
        return Exception

    @property
    def error_name(self) -> str:
        """Format the Name of the Error"""
        match len(bases := self.bases):
            case 1:
                front = f"{bases[0].__name__}"
            case 2:
                front = f"{bases[0].__name__[0:-5]}{bases[-1].__name__}"
        return f"{self.name}{front}"

    def message(self, data: ErrorSpec) -> str:
        """Format the Message of the Error"""
        return repr(data)

    @property
    def bases(self) -> Errors:
        """Distribute the registered Errors [1 SstCoreError, 0|1 Exception]"""
        sst_error: type[SstCoreError] = self.custom
        exception: type[Exception] | None = self.builtin
        return (sst_error,) if exception is None else (sst_error, exception)

    def compose(self) -> type[SstCoreError]:
        """Mix custom Error (MRO-left) to Builtin Exception"""
        bases: Errors = self.bases
        name: str = self.error_name
        return type(name, bases, {})
