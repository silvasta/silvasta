"""
Tuples assembled to Params

.
"""

__all__: list[str] = [
    "Var",
    "Args",
    "Kwargs",
    "Params",
    # types & protocols
    "VarsView",
    "KeyFormatting",
]

import builtins as _b
import collections.abc as _cabc
import typing as _typing
from collections.abc import Callable
from typing import Any, Literal, Self, SupportsIndex, TypeIs, overload

from .._types import Types as _T  # noqa:N814
from ..empty import VOID, MayNot
from . import _zero as _z
from ._frozen import frozendict
from ._tuplebase import (
    TupleBase,
    TupleField,
    merge_into_mapping,
    merge_into_sequence,
)
from ._tuples import NamedValue, SingleTuple, _Variadics

type VarsView = _typing.Literal["live", "dict", "frozen"]


class KeyFormatting(_typing.Protocol):
    def __call__(self, target: object, /) -> str:
        """Render the Value to a valid Key"""


class Feedable:
    """Enable `container @ func`, `func @ container`, and `a @ b @ func` stacking."""

    def feed[R](self, func: Callable[..., R], /) -> R:
        raise NotImplementedError(func)

    def params(self) -> Params:
        # IDEA: make @property like for list,tuple,set?
        raise NotImplementedError

    @_typing.overload
    def __matmul__(self, other: Feedable, /) -> Params: ...
    @_typing.overload
    def __matmul__[R](self, other: Callable[..., R], /) -> R: ...
    def __matmul__(self, other: Any, /) -> Any:
        """Check Feedable BEFORE callable() because Var defines __call__"""
        if isinstance(other, Feedable):
            return self.params() | other.params()
        if callable(other):
            return self.feed(other)
        return NotImplemented

    def __rmatmul__[R](self, func: Callable[..., R], /) -> R:
        return self.feed(func) if callable(func) else NotImplemented


class Var[T: Any = Any](NamedValue[T], Feedable, TupleBase):
    """Variable with Name and Value"""

    sep = TupleField[str]("=")
    keyformat = TupleField[KeyFormatting](lambda v: f"{v}")

    def __new__(cls, name: object, value: T, /) -> Self:
        if not isinstance(name, str):
            name: str = (
                cls.keyformat(func=lambda name: f"{name}")(name)
                if (formatter := cls.keyformat._default) is VOID
                else formatter(name)
            )
        return super().__new__(cls, name, value)

    def __call__(self, *args, **kwargs) -> Any:
        """Invoke the Value if callable or provide its Representation"""
        if callable(self.value):
            return self.value(*args, **kwargs)
        return f"Not Callable: {self}[{self.value!r}]"

    def feed[R](self, func: Callable[..., R], /) -> R:
        return func(**{self.name: self.value})

    def params(self) -> Params:
        return Params(kwargs=Kwargs({self.name: self.value}))

    @classmethod
    def is_unit(cls, item: object) -> TypeIs[Self]:
        return isinstance(item, cls)

    @classmethod
    def named(cls, item: Self | T, /) -> Self:
        return item if cls.is_unit(item) else cls(item, item)

    @classmethod
    def gettr(cls, target: object, name: str, /) -> Self:
        """Hit the Target with the Name to get the Attr"""
        return cls(name, getattr(target, name))


class Args[S: _cabc.Sequence = _T.Tuple](SingleTuple[S], Feedable, TupleBase):
    """Capture and Visualize Positional Parameter"""

    sep = TupleField[str](", ")
    icon = TupleField[str]("*")
    keyformat = TupleField[KeyFormatting](lambda v: f"{v}")

    @_typing.overload
    def __new__(cls) -> Args: ...
    @_typing.overload
    def __new__[Seq: _T.Seq](cls, data: Args[Seq], /) -> Args[Seq]: ...
    @_typing.overload
    def __new__[Seq: _T.Seq](cls, data: Seq, /) -> Args[Seq]: ...
    def __new__(cls, data=(), /):
        """Store one sequence in the single slot. Do not unpack it into slots."""
        match data:
            case _ if isinstance(data, cls):
                return data
            case _ if isinstance(data, (str, bytes, bytearray)):
                raise TypeError(
                    f"{cls.__name__}() expects a sequence, not {type(data).__name__}"
                )
            case _ if not isinstance(data, tuple):
                # LATER: make like a mode for tuple/list
                data: _T.Tuple = tuple(data)
        return tuple.__new__(cls, (data,))

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> Any: ...
    @overload
    def __getitem__(self, index: slice, /) -> tuple[Any, ...]: ...
    @overload
    def __getitem__(self, index: str, /) -> Any: ...
    def __getitem__(self, index: SupportsIndex | int | slice, /) -> Any:
        """Forward Index to inner Tuple"""
        if isinstance(index, (int, slice)):
            return self.data[index]
        return self.kwargs()[index]

    def __add__(self, other: Self | _cabc.Sequence) -> Self:
        match other:
            case _ if isinstance(other, type(self)):
                other_seq: _T.Seq = other.data
            case _ if _z.is_notext_iter(other):
                other_seq: _T.Seq = other
            case _:
                return NotImplemented
        return type(self)((*self.data, *other_seq))

    def __radd__[Seq: _cabc.Sequence](self, other: Seq) -> Seq:
        return (
            merge_into_sequence(other, self.data)
            if _z.is_notext_iter(other)
            else NotImplemented
        )

    def keys(self):
        return _cabc.KeysView({i: None for i, _ in enumerate(self)})

    def kwargs(self) -> Kwargs:
        """Transform Sequential Args into Mapped Kwargs (unwrapping Vars & deduplicating keys)."""
        out: dict[str, Any] = {}
        for item in self.data:
            name, val = (
                (self.keyformat(item), item)
                if not isinstance(item, Var)
                else item
            )
            out[_z.uniqued(name, out)] = val
        return Kwargs(**out)

    def feed[R](self, func: Callable[..., R], /) -> R:
        return func(*self)

    def params(self) -> Params:
        return Params(self)

    if _typing.TYPE_CHECKING:  # CHECK: still needed without TupleBase.mix?

        @classmethod
        def create[Seq: _T.Seq](
            cls, args: MayNot[Seq | Args[Seq]] = None
        ) -> Args[Seq]: ...

    @classmethod
    def absorb(cls, *args) -> Self:
        return cls(args)

    @classmethod
    def slots(cls, target: object, /) -> Self:
        """Build from __slots__ of Target"""
        return cls(
            tuple(
                Var.gettr(target, slot) for slot in _z.iter_slot_names(target)
            )
        )


type _KeyFilter = _cabc.Set[str] | _cabc.Mapping[str, Any] | Kwargs[Any]


class Kwargs[M: _T.Map](SingleTuple[M], Feedable, TupleBase):
    """Capture and Visualize Keyword Parameter"""

    sep = TupleField[str](", ")
    icon = TupleField[str]("**")

    @property
    def frozen(self):
        return frozendict(self.data)

    @property
    def dict(self):
        return _b.dict(self.data)

    @_typing.overload
    def __new__(cls) -> Kwargs[frozendict[str, Any]]: ...
    @_typing.overload
    def __new__[M2: _T.StrMap](cls, data: Kwargs[M2], /) -> Kwargs[M2]: ...
    @_typing.overload
    def __new__[M2: _T.StrMap](cls, data: M2, /) -> Kwargs[M2]: ...
    @_typing.overload
    def __new__(cls, /, **pairs: Any) -> Kwargs[_T.StrDict]: ...
    def __new__(cls, data: Any = VOID, /, **pairs: Any) -> Any:
        """Store one mapping in the single slot. Never iterate it into slots."""
        match data:
            case _ if data is VOID:
                return tuple.__new__(cls, (pairs or frozendict(),))
            case _ if pairs:
                raise TypeError(
                    f"{cls.__name__}() takes a mapping or keywords, not both"
                )
            case _ if isinstance(data, cls):
                return data
            case _ if not isinstance(data, _cabc.Mapping):
                raise TypeError(
                    f"{cls.__name__}() expected a mapping, got {type(data).__name__}"
                )
        return tuple.__new__(cls, (data,))

    @overload
    def _normalize(
        self, target: object, /, *, _set: Literal[False] = False
    ) -> _T.Map | VOID: ...
    @overload
    def _normalize(
        self, target: object, /, *, _set: Literal[True]
    ) -> _T.Map | _cabc.Set | VOID: ...
    def _normalize(
        self, target: object, /, *, _set: bool = False
    ) -> _T.Map | _cabc.Set | VOID:
        """Prepare Key or Map for Operator"""
        match target:
            case _ if isinstance(target, type(self)):
                return target.data
            case _ if isinstance(target, _cabc.Mapping):
                return target
            case _ if _set and isinstance(target, _cabc.Set):
                return target
            case _:
                return VOID

    def __or__(self, other: Self | _T.Map, /) -> Self:
        if (other_map := self._normalize(other)) is VOID:
            return NotImplemented
        _merged = merge_into_mapping(self.data, other_map)
        if _merged is NotImplemented:
            _merged: _T.Map = {**self.data, **other_map}
        return type(self)(_merged)

    @_typing.overload
    def __ror__[K, V](
        self, other: _b.dict[K, V], /
    ) -> _b.dict[K | str, V | Any]: ...
    @_typing.overload
    def __ror__[T: _T.Map](self, other: T, /) -> T: ...
    def __ror__(self, other: _T.Map, /) -> Any:
        if _typing.TYPE_CHECKING:
            other: Any = other
        return (
            merge_into_mapping(other, self.data)
            if isinstance(other, _cabc.Mapping)
            else NotImplemented
        )

    def __and__(self, other: _KeyFilter, /) -> Self:
        if (keys := self._normalize(other, _set=True)) is VOID:
            return NotImplemented
        return type(self)({k: v for k, v in self.data.items() if k in keys})

    def __sub__(self, other: _KeyFilter, /) -> Self:
        if (keys := self._normalize(other, _set=True)) is VOID:
            return NotImplemented
        return type(self)({k: v for k, v in self.data.items() if k not in keys})

    def __iter__(self) -> _cabc.Iterator[Var]:  # ty:ignore
        for name, value in self.data.items():
            yield Var(name, value)

    @overload
    def __getitem__(self, key: SupportsIndex, /) -> Any: ...
    @overload
    def __getitem__(self, key: slice, /) -> tuple[Any, ...]: ...
    @overload
    def __getitem__(self, key: str, /) -> Any: ...
    def __getitem__(self, key: str | int) -> Any:
        if isinstance(key, (int, slice)):
            return self[tuple(self.keys())[key]]
        return self.data[key]

    def keys(self) -> _cabc.KeysView[str]:
        return self.data.keys()

    def args(self) -> Args:
        """Transform Mapped Kwargs into Sequential Args of Vars."""
        return Args(tuple(self))

    def feed[R](self, func: Callable[..., R], /) -> R:
        return func(**self.data)

    def params(self) -> Params:
        return Params(kwargs=self)

    if _typing.TYPE_CHECKING:  # CHECK: still needed without TupleBase.mix?

        @classmethod
        def create(
            cls, kwargs: MayNot[_T.StrMap | Kwargs[Any]] = None
        ) -> Kwargs[Any]: ...

    @classmethod
    def absorb(cls, **kwargs) -> Self:
        return cls(kwargs)

    @classmethod
    def vars(cls, target, /, *, view: VarsView = "dict") -> Kwargs:
        """Build from vars of Target - direct reference with live_view"""
        match view:
            case "live":
                return cls(vars(target))
            case "dict":
                return cls(dict(vars(target)))
            case "frozen":
                return cls(frozendict(vars(target)))

    @classmethod
    def slots(cls, target: object, /, *, frozen: bool = False) -> Kwargs:
        """Build from __slots__ of Target as a Mapping."""
        data: _T.StrDict = {
            name: val
            for name in _z.iter_slot_names(target)
            if (val := getattr(target, name, VOID)) is not VOID
        }
        return cls(frozendict(data) if frozen else data)


_EMPTY_ARGS: Args = Args()
_EMPTY_KWARGS: Kwargs = Kwargs()


class Params[A: _cabc.Sequence[Any] = _T.Tuple, K: _T.Map = _T.StrDict](
    _Variadics[Args[A], Kwargs[K]], Feedable, TupleBase
):
    """Capture and Visualize 1 Signature"""

    sep = TupleField[str](", ")
    icon = TupleField[str]("***")

    @_typing.overload
    def __new__(cls, args: Self, /) -> Self: ...
    @_typing.overload
    def __new__(
        cls,
        args: Args[Any] | _cabc.Iterable[Any] = _EMPTY_ARGS,
        kwargs: Kwargs[Any] | _T.StrMap = _EMPTY_KWARGS,
    ) -> Self: ...
    def __new__(cls, args: Any = _EMPTY_ARGS, kwargs: Any = _EMPTY_KWARGS):
        if isinstance(args, cls):
            if kwargs is _EMPTY_KWARGS:
                return args
            raise TypeError(
                f"{cls.__name__}() cannot take kwargs with a {cls.__name__} instance"
            )
        if not isinstance(args, Args):
            args: Args = Args(args)
        if not isinstance(kwargs, Kwargs):
            kwargs: Kwargs = Kwargs(kwargs)
        return tuple.__new__(cls, (args, kwargs))

    def __or__(self, other: Params | Kwargs[Any] | _T.StrMap, /) -> Self:
        """Merge two Params (concatenating args and updating kwargs)."""
        if _typing.TYPE_CHECKING:
            other: Any = other
        if isinstance(other, Params):
            return type(self)(
                self.args + other.args, self.kwargs | other.kwargs
            )
        if isinstance(other, (Kwargs, _cabc.Mapping)):
            return type(self)(self.args, self.kwargs | other)
        return NotImplemented

    def __ror__(self, other: Kwargs[Any] | _T.StrMap, /) -> Self:
        if _typing.TYPE_CHECKING:
            other: Any = other
        if isinstance(other, (Kwargs, _cabc.Mapping)):
            return type(self)(self.args, Kwargs(other) | self.kwargs)
        return NotImplemented

    def __add__(self, other: Args[Any] | _cabc.Sequence[Any], /) -> Self:
        if _z.is_notext_iter(other):
            return type(self)(self.args + other, self.kwargs)
        return NotImplemented

    def __radd__(self, other: Args[Any] | _cabc.Sequence[Any], /) -> Self:
        if isinstance(other, Args) or (
            not isinstance(other, TupleBase) and _z.is_notext_iter(other)
        ):
            return type(self)(Args(other) + self.args, self.kwargs)
        return NotImplemented

    def __sub__(self, other: _KeyFilter, /) -> Self:
        if _typing.TYPE_CHECKING:
            other: Any = other
        if isinstance(other, (Kwargs, _cabc.Set, _cabc.Mapping)):
            return type(self)(self.args, self.kwargs - other)
        return NotImplemented

    def __bool__(self) -> bool:
        return bool(self.args) or bool(self.kwargs)

    def __iter__(self) -> _cabc.Iterator[Any]:
        yield from self.args

    @overload
    def __getitem__(self, key: SupportsIndex, /) -> Any: ...
    @overload
    def __getitem__(self, key: slice, /) -> tuple[Any, ...]: ...
    @overload
    def __getitem__(self, key: str, /) -> Any: ...
    def __getitem__(self, key: str) -> Any:
        return self.kwargs[key]

    def keys(self) -> _cabc.KeysView[str]:
        return self.kwargs.keys()

    def joins(self) -> _cabc.Iterator:
        yield from self.args
        yield from self.kwargs

    def feed[R](self, func: Callable[..., R], /) -> R:
        """Apply captured *args,**kwargs to Function"""
        return func(*self, **self)

    if _typing.TYPE_CHECKING:  # CHECK: still needed without TupleBase.mix?

        @classmethod
        def create(
            cls,
            args: MayNot[_cabc.Iterable[Any] | Args[Any]] = None,
            kwargs: MayNot[_T.StrMap | Kwargs[Any]] = None,
        ) -> Self: ...

    @classmethod
    def absorb(cls, *args, **kwargs) -> Self:
        return cls(Args(args), Kwargs(kwargs))

    @classmethod
    def inspect(cls, target: object, /, *, view: VarsView = "dict") -> Self:
        """Capture both __slots__ (in args) and vars() (in kwargs) of Target."""
        return cls(
            args=Args.slots(target), kwargs=Kwargs.vars(target, view=view)
        )
