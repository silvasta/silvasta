"""
Adapt the SstError to PortLink

- This is intends as the one and only Raiser Implementation in the port
- Still experimental, like the setups outside the port

                                  DependencyLevel.sstcore.port[0.X]
"""

__all__: list[str] = [
    "SstError",
    "mix_error",
    "rebuild",
    "RaiserMeta",
    "RaiserField",
    "SstPortError",
    #
    "FailedHackError",
    "RaiserField",
    "RaiserMeta",
]

import copyreg
from collections.abc import Callable, Iterator, Mapping, Sequence
from functools import cache
from typing import Any, NamedTuple, Self

from ._types import Types as _T  # noqa:N814
from ._types import _LockedClsMeta
from .empty import MayNot, MayNotCls
from .primitives import Args, Kwargs, Params, Var

type ErrorClosure = Callable[[type[Exception]], type[SstError]]


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

    def __repr__(self) -> str:
        return f"{self.name}[({self.params!r})]"

    @classmethod
    def weave(
        cls,
        builtin: MayNotCls[Exception] = None,
        *,
        prefix: str = "",
        module: str = "",
    ) -> type[Self]:
        """Mix the Error with a builtin Exception (cached and picklable)"""

        if builtin is None and not prefix:
            return cls

        _name = _error_name(cls, builtin, prefix)
        _bases = (cls, builtin) if builtin else (cls,)
        _module = (module or cls.__module__,)

        return mix_error(_name, _bases, _module)  # ty:ignore


@cache
def mix_error(
    name: str, bases: _T.Errors, module: str = "", /
) -> type[SstError]:
    """Dynamically create and cache a picklable Exception Class"""

    def _reduce(self: Exception) -> tuple[Any, ...]:
        state: dict[str, Any] | None = self.__dict__ or None
        return (rebuild, (name, bases, module, self.args), state)

    namespace: dict[str, Any] = {
        "__module__": module or __name__,
        "__qualname__": name,
        "__reduce__": _reduce,
        "_weave_spec": (name, bases, module),
    }
    return _ErrorWeaverMeta(name, bases, namespace)  # ty:ignore


def rebuild(name: str, bases: _T.Errors, module: str, args: tuple) -> SstError:
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


#  LINE: -- Formatting -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _error_name(
    custom: type[SstError],
    root: MayNotCls[Exception] = None,
    /,
    prefix: str = "",
) -> str:
    """Create target Error Name out of 2 Exception Names"""
    return (
        f"{prefix}{_error_stem(custom)}{root.__name__}"
        if root
        else f"{prefix}{custom.__name__}"
    )


def _error_stem(cls: type[Exception], /) -> str:
    """Extract Error Name Part"""
    return cls.__name__[:-5] if cls.__name__.endswith("Error") else cls.__name__


def _raiser_prefix(raiser: type, /) -> str:
    """Extract Raiser Name Part"""
    return raiser.__name__.removesuffix("Raiser")


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


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class RaiserField[**P]:
    """Wire error name, owner class, and provide message template"""

    @property
    def sst_error(self) -> type[SstError]:
        """Use Custom Error (from __init__) or base_error from Raiser"""
        return (
            self.custom_error
            if self.custom_error is not None
            else self.base_error
            if self.base_error is not None
            else SstError
        )

    def __new__[E: Exception](cls, *_args, **_kwargs) -> Callable[P, SstError]:
        """Perfectly annotate Field on Locked Cls Body"""
        return super().__new__(cls)  # ty:ignore

    def __init__[E: Exception](
        # IDEA: accept defaults that can be used for empty rendering!
        # - meaning the error can be displayed in CLI with mock data
        self,
        builtin_error: type[E],
        template: str,
        /,
        ___defaults: Any = None,
        *,
        processor: MayNot[Callable[P, Any]] = None,
        sst_error: MayNotCls[SstError] = None,
    ):
        """Fill all tools, processor intended for multiple purposes"""

        self.builtin_error: type[Exception] = builtin_error
        self.template: str = template
        self.name: str = ""
        self.processor: MayNot[Callable[P, Any]] = processor
        self.custom_error: MayNotCls[SstError] = sst_error

    def __str__(self):
        return f"{self.owner.__name__}.{self.name}"

    def __set_name__(self, owner: type, name: str) -> None:
        """Extract owner data including Error and bind it"""
        self.owner = owner
        self.name: str = name
        self.base_error: MayNotCls[SstError] = getattr(
            owner, "base_error", None
        )

        def _weave_with_owner_data(error: type[Exception], /) -> type[SstError]:
            return self.sst_error.weave(
                builtin=error,
                prefix=_raiser_prefix(owner),
                module=owner.__module__,
            )

        self.weave: ErrorClosure = _weave_with_owner_data
        self.mixed_error: type[SstError] = self.weave(self.builtin_error)

    def __call__(self, func: Callable[P, Any], /) -> Self:
        """Expose with Function Signature and custom Processing"""
        self.processor: Callable[P, Any] = func
        if not self.name:  # AI: when can this happen?
            self.name: str = getattr(func, "__name__", "")
        return self

    def __get__(self, _unit: Any, _host: MayNotCls) -> Callable[P, SstError]:
        return self._pipeline_assemble

    def _pipeline_assemble(self, *args, **kwargs):
        """Route Payloud trough Process and Format"""
        params = Params(Args(args), Kwargs(kwargs))
        dto: RaiserDTO = self._process(params)
        text: str = self._format(*dto.text_pa, **dto.text_kw)
        message: str = self._redact(text)
        return self.mixed_error(message, *dto.error_posarg, **dto.error_keyarg)

    def _process(self, params) -> RaiserDTO:
        """Split, sort and assemble the incoming params"""
        # TODO: as well other branches that e.g. don't need the DTO
        if self.processor is None:
            return RaiserDTO(
                error_posarg=Args(),
                error_keyarg=params.kwargs,
                text_pa=params.args,
                text_kw=Kwargs(),
            )
        return self.processor(params)  # ty:ignore FIX: typinjg

    def _format(self, *args, **kwargs) -> str:
        """Create the message Text"""
        return self.template.format(*args, **kwargs)

    def _redact(self, text: str) -> str:
        """Create the final Layout"""
        return f"[{self}] {text}".strip()


class RaiserDTO(NamedTuple):
    error_posarg: Args
    error_keyarg: Kwargs
    text_pa: Args
    text_kw: Kwargs

    @classmethod
    def empty(
        cls,
        error_posarg: MayNot[Sequence] = None,
        error_keyarg: MayNot[Mapping] = None,
        text_pa: MayNot[Sequence] = None,
        text_kw: MayNot[Mapping] = None,
    ) -> Self:
        return cls(  # EXTRACT: maybe to Params?
            Args(error_posarg or ()),
            Kwargs(error_keyarg or {}),
            Args(text_pa or ()),
            Kwargs(text_kw or {}),
        )


class RaiserMeta(_LockedClsMeta, type):
    """Equip Raiser classes with iteration and error formatting"""

    _name: str = "Error"
    _error: type[SstError] = SstError

    @property
    def base_error(cls) -> type[SstError]:
        return cls._error

    def _meta_and_cls_attrs(cls) -> dict[str, Any]:
        return {**type(cls).__dict__, **cls.__dict__}

    def __iter__(cls) -> Iterator[Var]:
        for name in cls._meta_and_cls_attrs():
            if not name.startswith("_"):
                yield Var.gettr(cls, name)
