"""
Install the Cached Mixing Setup for the SstError

- SstError: root of all Errors
- SstPortError: root of all Errors launched inside the port

- Raiser: MetaClass with Fields to collect and distribute Error Definitions

                                  DependencyLevel.sstcore.port[0:2]
"""

__all__: list[str] = [
    "SstError",
    "mix_error",  # cached factory
    "SstPortError",
    "FailedHackError",
    # raising
    "RaiserMeta",
    "RaiserField",
    "RaiserParams",
    "ErrorProducer",
    "ErrorProcessor",
    # type guarding
    "is_raiser",
    "is_ssterror",
    "is_ssterror_cls",
    "is_porterror",
    "is_porterror_cls",
]

import copyreg
import typing as _typing
from collections.abc import Callable, Iterable, Iterator
from functools import cache
from typing import Any, Self, Unpack

from ._types import Types as _T  # noqa:N814
from ._types import _LockedClsMeta
from .empty import MayNot, MayNotCls
from .primitives import Args, Kwargs, NameParser, Params, TupleBase, Var


class SstError(Exception):
    """The Root of all sst Exceptions"""

    def __init__(self, text: str = "", /, *args, **kwargs) -> None:
        """Text the final Message and Capture all Arg/Kwargs"""
        if text:
            self.params: Params = Params.absorb(text, *args, **kwargs)
            super().__init__(text)
        else:
            self.params: Params = Params.absorb(*args, **kwargs)
            if self.params:
                super().__init__(self.params)
            else:
                super().__init__()

    @property
    def name(self) -> str:
        return type(self).__name__

    __str__ = Exception.__str__  # avoid 'KeyError.__str__ brackets'

    def __repr__(self) -> str:
        return f"{self.name}[({self.params!r})]"

    @_typing.overload
    @classmethod
    def weave[BuiltinError: Exception](
        cls, builtin: type[BuiltinError], **tkw: Unpack[_WeaveInput]
    ) -> type[_WovenError[Self, BuiltinError]]: ...
    @_typing.overload
    @classmethod
    def weave(cls, builtin: None, **tkw: Unpack[_WeaveInput]) -> type[Self]: ...

    @classmethod
    def weave[BuiltinError: Exception](
        cls, builtin: MayNotCls[BuiltinError] = None, **tkw: Unpack[_WeaveInput]
    ) -> type[_MixedError[Self, BuiltinError]]:
        """Mix the Error with a builtin Exception (cached and picklable)"""

        if builtin is None and not tkw.get("prefix"):
            return cls

        name: str = _error_name(cls, builtin, **tkw)
        bases: tuple[type, ...] = (cls, builtin) if builtin else (cls,)
        module: str = tkw.get("module", cls.__module__)

        return mix_error(name, bases, module)  # ty:ignore


@cache
def mix_error(
    name: str, bases: _T.Errors, module: str = "", /
) -> type[SstError]:
    """Dynamically create and cache a picklable Exception Class"""

    def _reduce(self: Exception) -> tuple[Any, ...]:
        state: dict[str, Any] | None = self.__dict__ or None
        return (_rebuild, (name, bases, module, self.args), state)

    namespace: dict[str, Any] = {
        "__module__": module or __name__,
        "__qualname__": name,
        "__reduce__": _reduce,
        "_weave_spec": (name, bases, module),
    }
    return _ErrorWeaverMeta(name, bases, namespace)  # ty:ignore


def _rebuild(name: str, bases: _T.Errors, module: str, args: tuple) -> SstError:
    """Top-level pickle hook to rebuild a dynamically mixed exception"""
    cls: type[SstError] = mix_error(name, bases, module)
    error: SstError = cls.__new__(cls)
    error.args = args
    return error


class _ErrorWeaverMeta(type):
    """Give dynamically woven classes a tiny metaclass to register a reducer"""

    _weave_spec: tuple[str, _T.Errors, str]


def _reduce_woven_cls(cls: _ErrorWeaverMeta) -> tuple[Any, ...]:
    return (mix_error, cls._weave_spec)


copyreg.pickle(_ErrorWeaverMeta, _reduce_woven_cls)


#  LINE: -- Implementations -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SstPortError(SstError):
    """Match and Catch all Errors in the lowest Port Layers"""


class FailedHackError(SstError):
    """
    It was a nice try, but...

    (I hope I don't have to  explain that this is mostly for internal tests...)
    """

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__("...I told you it will fail!", *args)


#  LINE: -- Type Guarding -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def is_raiser(target: object, /) -> _typing.TypeIs[RaiserMeta]:
    """Is the Target a Class Instance of the RaiserMeta?"""
    return isinstance(target, RaiserMeta)


def is_ssterror_cls(target: object, /) -> _typing.TypeIs[type[SstError]]:
    """Is the Target a Subclass of the SstError?"""
    return isinstance(target, type) and issubclass(target, SstError)


def is_ssterror(target: object, /) -> _typing.TypeIs[SstError]:
    """Is the Target an Instance of the SstError?"""
    return isinstance(target, SstError)


def is_porterror_cls(target: object, /) -> _typing.TypeIs[type[SstPortError]]:
    """Is the Target a Subclass of the SstError?"""
    return isinstance(target, type) and issubclass(target, SstPortError)


def is_porterror(target: object, /) -> _typing.TypeIs[SstPortError]:
    """Is the Target an Instance of the SstError?"""
    return isinstance(target, SstPortError)


#  LINE: -- Formatting -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _error_name(
    custom: type[SstError],
    root: MayNotCls[Exception] = None,
    /,
    **tkw: Unpack[_ErrorNameInput],
) -> str:
    """Create target Error Name out of 2 Exception Names"""
    _prefix, _middle = tkw.get("prefix", ""), tkw.get("middle", "")
    return (
        f"{_prefix}{_error_stem(custom)}{_middle}{root.__name__}"
        if root
        else f"{_prefix}{custom.__name__}{_middle}"
    )


def _error_stem(cls: type[Exception], /) -> str:
    """Extract Error Name Part"""
    return cls.__name__[:-5] if cls.__name__.endswith("Error") else cls.__name__


def _raiser_prefix(raiser: type, /) -> str:
    """Extract Raiser Name Part"""
    return raiser.__name__.removesuffix("Raiser")


#  LINE: -- Input, Alias and Definitions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _ErrorNameInput(_typing.TypedDict, total=False):
    prefix: str
    middle: str


class _WeaveInput(_ErrorNameInput, total=False):
    module: str


type _ErrorWeaver[
    SE: SstError,
    BE: Exception,
] = Callable[[type[BE]], type[_MixedError[SE, BE]]]


type _WovenError[SE: SstError, BE: Exception] = SE & BE  # ty:ignore

type _MixedError[SE: SstError, BE: Exception] = SE | _WovenError[SE, BE]


class ErrorProducer[**P, WE: SstError = SstError](_typing.Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> WE:
        """Fill the weaved Error with the final Params"""


class ErrorProcessor[**P](_typing.Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> RaiserParams:
        """Preparete the Params before Error Assembly"""


#  LINE: -- Raiser -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class RaiserField[**P, SE: SstError = SstError, BE: Exception = Exception]:
    """Wire error name, owner class, and provide message template"""

    _default_error: type[SstError] = SstError

    class _Extras(_typing.TypedDict):
        processor: MayNot[Callable[P, Any]]
        sst_error: MayNotCls[SE]

    @classmethod
    def deco[**P2, BE2: Exception, SE2: SstError = SstError](
        cls,
        builtin_error: type[BE],
        template: str,
        /,
        test_input: tuple[object, ...] = (),
        *,
        sst_error: MayNotCls[SE2] = None,
    ) -> Callable[[Callable[P2, RaiserParams]], RaiserField[P2, SE2, BE2]]:
        # LATER: decorators for different configuration
        # - either handling the params, the entire formatting, something else
        def _bind(
            func: Callable[P2, RaiserParams], /
        ) -> RaiserField[P2, SE2, BE2]:
            return RaiserField(
                builtin_error,
                template,
                test_input,
                processor=func,
                sst_error=sst_error,
            )

        return _bind

    def __init__(
        self,
        builtin_error: type[BE],
        template: str,
        /,
        test_input: tuple[object, ...] = (),
        *,
        processor: MayNot[Callable[P, Any]] = None,
        sst_error: MayNotCls[SE] = None,
    ):
        """Fill all tools, processor intended for multiple purposes"""

        self.builtin_error: type[BE] = builtin_error
        self.name_parser = NameParser(pattern=template)  # LATER: cls attribute

        self.test_input: tuple[object, ...] = test_input  # LATER: validate

        self.processor: MayNot[ErrorProcessor[P]] = processor
        self._sst_error: MayNotCls[SE] = sst_error

        self.name: str = ""  # ensure always available

    def __str__(self):
        return f"{self.owner.__name__}.{self.name}"

    def __repr__(self):
        # rr = [
        #     "--- b",
        #     f"{self}[{Kwargs.vars(self):b}]",
        #     "--- i",
        #     f"{self}[{Kwargs.vars(self):i}]",
        #     "--- n",
        #     f"{self}[{Kwargs.vars(self):n}]",
        #     "--- v",
        #     f"{self}[{Kwargs.vars(self):v}]",
        #     "--- nv",
        #     f"{self}[{Kwargs.vars(self):nv}]",
        # ]
        # return "\n".join(rr)
        return f"{self}[{Kwargs.vars(self):nv}]"  # PARAM: FORMAT

    def __set_name__(self, owner: type, name: str) -> None:
        """Extract data from owner(=Raiser) including Error and bind it"""
        self.owner: type = owner
        self.name: str = name

        def _weave_with_owner_data(
            error: type[BE], /
        ) -> type[_MixedError[SE, BE]]:
            return self.sst_error.weave(
                builtin=error,
                middle=owner.__name__,
                module=owner.__module__,
            )

        self.weave: _ErrorWeaver[SE, BE] = _weave_with_owner_data
        self.mixed_error: type[_MixedError[SE, BE]] = self.weave(
            self.builtin_error
        )

    @_typing.overload
    def __get__(self, unit: None, _raiser: type) -> Self: ...
    @_typing.overload
    def __get__(
        self, unit: object, _raiser: type
    ) -> ErrorProducer[P, _MixedError[SE, BE]]: ...
    def __get__(
        self, unit: MayNot, _raiser: type
    ) -> ErrorProducer[P, _MixedError[SE, BE]] | Self:
        """Basically No-Op as Unit is always None (when used with Raiser)"""
        return self if unit is None else self._pipeline_assemble

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> _MixedError[SE, BE]:
        """Assemble the woven SstError instance"""
        return self._pipeline_assemble(*args, **kwargs)

    def assemble_test(self, **error_kwargs) -> _MixedError[SE, BE]:
        return self._pipeline_assemble(*self.test_input, **error_kwargs)

    def _pipeline_assemble(self, *args, **kwargs) -> _MixedError[SE, BE]:
        """Route Payloud trough Process and Format"""
        params = Params(Args(args), Kwargs(kwargs))
        _demo_of_absorb_params = Params.absorb(*args, **kwargs)
        prepared: RaiserParams = self._process(params)

        text: str = self._format(params=prepared.text)
        message: str = self._redact(text)

        return self.mixed_error(message, *prepared.error, **prepared.error)

    def _redact(self, text: str) -> str:
        """Create the final Layout"""
        return f"[{self}] {text}".strip()

    def _format(self, params: Params) -> str:
        """Create the message Text"""
        # print(f"{params=}")
        if params.args and params.kwargs:
            raise NotImplementedError("Insert either args or kwargs")
        return self.name_parser(
            params.args.tuple if params.args else params.kwargs.dict
        )

    def _process(self, params: Params) -> RaiserParams:
        """Split, sort and assemble the incoming params"""
        if self.processor is None:
            return RaiserParams.create(
                text_args=params.args,
                error_kwargs=params.kwargs,
            )
        return params.feed(self.processor)

    @property
    def sst_error(self) -> type[SE]:
        """Use SstError injected in Init, extracted from Raiser or Default"""
        return (
            self._sst_error
            if self._sst_error is not None
            else self.raiser_error
            if self.raiser_error is not None
            else self.default_error  # ty:ignore (cast SstError -> SE)
        )

    @property
    def raiser_error(self) -> MayNotCls[SstError]:
        """Access the SstError mounted on the Raiser"""
        if is_raiser(self.owner):
            return self.owner.raiser_error

    @property
    def default_error(self) -> type[SstError]:
        """Ensure at least one Error is available + Subhook to overwrite"""
        return self._default_error

    @default_error.setter
    def default_error(self, error: SE | type[SE]) -> None:
        """Ensure at least one Error is available + Subhook to overwrite"""
        match error:
            case _ if is_ssterror_cls(error):
                self._default_error: type[SE] = error
            case _ if is_ssterror(error):
                self._default_error: type[SE] = type(error)
            case _:
                raise TypeError(f"[{self}] Invalid Assignment: {error=}")


class RaiserParams1(_typing.NamedTuple):
    """Handle incoming Params for Message and for Exception"""

    text: Params
    error: Params


@TupleBase.mix
class RaiserParams(_typing.NamedTuple):
    """Handle incoming Params for Message and for Exception"""

    text: Params
    error: Params

    if _typing.TYPE_CHECKING:

        @classmethod
        def create(
            cls,
            text: MayNot[Params] = None,
            error: MayNot[Params] = None,
            *,
            text_args: MayNot[Iterable[Any] | Args[Any]] = None,
            text_kwargs: MayNot[_T.StrMap | Kwargs[Any]] = None,
            error_args: MayNot[Iterable[Any] | Args[Any]] = None,
            error_kwargs: MayNot[_T.StrMap | Kwargs[Any]] = None,
        ) -> Self: ...


class RaiserMeta(_LockedClsMeta, type):
    """Equip Raiser classes with iteration and error formatting"""

    _name: str = "Error"
    _error: type[SstError] = SstError

    @property
    def raiser_error(cls) -> type[SstError]:
        return cls._error

    def _meta_and_cls_attrs(cls) -> dict[str, Any]:
        return {**type(cls).__dict__, **cls.__dict__}

    def __iter__(cls) -> Iterator[Var]:
        for name, value in cls._meta_and_cls_attrs().items():
            if not name.startswith("_") and callable(value):
                yield Var.gettr(cls, name)
