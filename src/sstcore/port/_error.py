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
    "FailedDispatchError",
    "FailedHackError",
    "EnumError",
    "RaiserField",
    "RaiserMeta",
]

import copyreg
from collections.abc import Callable, Iterator
from enum import Enum
from functools import cache
from typing import Any, Self

from ._types import Types as _T  # noqa:N814
from ._types import _LockedClsMeta
from .empty import MayNotCls
from .primitives import Params, Var
from .solid import BaseEnum


class SstError(Exception):
    """The Root of all sst Exceptions"""

    def __init__(self, text: str = "", /, *args, **kwargs) -> None:
        """Handle final Message and Arg/Kwarg assignment"""

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
        builtin: MayNotCls[Exception] = None,  # CHECK: MayNotClsype better?
        *,
        prefix: str = "",
        module: str = "",
    ) -> type[Self]:
        """Mix the Error with a builtin Exception (cached and picklable)"""

        if builtin is None and not prefix:
            return cls

        return mix_error(
            _error_name(cls, builtin, prefix),
            (cls, builtin) if builtin else (cls,),
            module or cls.__module__,
        )  # ty:ignore


class _WovenErrorMeta(type):
    """Give dynamically woven classes a tiny metaclass to register a reducer"""

    _weave_spec: tuple[str, _T.Errors, str]


def _reduce_woven_cls(cls: _WovenErrorMeta) -> tuple[Any, ...]:
    return (mix_error, cls._weave_spec)


copyreg.pickle(_WovenErrorMeta, _reduce_woven_cls)


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
    return _WovenErrorMeta(name, bases, namespace)  # ty:ignore


def rebuild(name: str, bases: _T.Errors, module: str, args: tuple) -> SstError:
    """Top-level pickle hook to rebuild a dynamically mixed exception"""
    cls: type[SstError] = mix_error(name, bases, module)
    error: SstError = cls.__new__(cls)
    error.args = args
    return error


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


def _raiser_prefix(raiser: type, /) -> str:  # CHECK: deterministic enough?
    """Extract Raiser Name Part"""
    return raiser.__name__.removesuffix("Raiser")


#  LINE: -- Implementations -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SstPortError(SstError):
    """Match and Catch all Errors in the lowest Port Layers"""


class FailedDispatchError(SstError, NotImplementedError):
    # LATER: sync with NotImplementedDispatchError(sstcore.error.SstCoreError)
    """Raise on missing TargetType for singledispatch(method)"""

    def __init__(self, first: Any, *args: Any, **kwargs):
        self.first = first
        msg = f"Missing dispatch target for {type(first).__name__}"
        super().__init__(msg, *(first, *args), **kwargs)


class FailedHackError(SstError):
    """
    It was a nice try, but...

    (I hope I don't have to  explain that this is mostly for internal tests...)
    """

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__("...I told you it will fail!", *args)


class EnumError(SstError, TypeError):
    # MOVE: solid? structures._enum (and mount to BaseEnum)?
    """Temporary Resolve the SstEnumMeta blinding"""

    def __init__(
        self, member_or_cls: Enum | type[Enum], /, reason="", *args
    ) -> None:
        """Forward Args to Exception"""
        reason: str = reason or "Failed"
        match BaseEnum.membership(member_or_cls):
            case ():
                who = f"Unknown: {member_or_cls=}"
            case (enum_cls,):
                self.enum: type[BaseEnum] = enum_cls
                who = f"BaseEnum: {enum_cls}"
            case (enum_cls, member):
                self.enum: type[BaseEnum] = enum_cls
                self.member: BaseEnum = member
                who = f"BaseEnum: {enum_cls=}, {member=}"
        super().__init__(f"{who} | {reason=}", *args)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class RaiserField[**P]:
    """Wire error name, owner class, and provide message template"""

    def __new__[E: Exception](cls, *_args, **_kwargs) -> Callable[P, SstError]:
        return super().__new__(cls)  # ty:ignore

    def __init__[E: Exception](
        self,
        error_type: type[E],
        template: str,
        /,
        *,
        preprocess: Callable[P, Any] | None = None,
    ):
        self.raw_error: type[Exception] = error_type
        self.error_type: type[SstError] = SstPortError.weave(error_type)
        self.template: str = template
        self.preprocess: Callable[P, Any] | None = preprocess
        self.name: str = ""

    def __call__(self, func: Callable[P, Any], /) -> Self:
        """Allow @ErrorClsField(TypeError, '...') decorator syntax for preprocessing."""
        self.preprocess = func  # IMPORTANT: add desired behaviour
        if not self.name:
            self.name = getattr(func, "__name__", "")
        return self

    def __set_name__(self, owner: type, name: str) -> None:
        self.owner = owner
        self.name = name
        base_err: type[SstError] = getattr(owner, "_base_error", SstError)
        self.error_type: type[SstError] = base_err.weave(
            self.raw_error,  # NEXT:
            prefix=_raiser_prefix(owner),
            module=owner.__module__,
        )

    def __str__(self):
        return f"{self.owner.__name__}.{self.name}"

    def _build(self, *args, **kwargs):
        """Format payload from positional/keyword args if provided"""

        if self.preprocess is not None:  # FIX: with desired behaviour
            args, kwargs = self.preprocess(*args, **kwargs)

        message = f"[{self}] {self.template.format(*args, **kwargs)}"

        return self.error_type(message.strip())

    def __get__(self, _unit: Any, _host: MayNotCls) -> Callable[P, SstError]:
        return self._build


class RaiserMeta(_LockedClsMeta, type):
    """Equip Raiser classes with iteration and error formatting"""

    _name: str = "Error"

    def _meta_and_cls_attrs(cls) -> dict[str, Any]:
        return {**type(cls).__dict__, **cls.__dict__}

    def __iter__(cls) -> Iterator[Var]:
        for name in cls._meta_and_cls_attrs():
            if not name.startswith("_"):
                yield Var.gettr(cls, name)
