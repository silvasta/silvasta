"""
Most basic parts

.
"""

__all__: list[str] = [
    "Var",
    "Args",
    "Kwargs",
    "Params",
    # control & bases
    "TupleControl",
    "NamedValue",
    "SingleTuple",
    "Variadics",
    # types & protocols
    "VarsView",
    "KeyFormatting",
]

import builtins as _b
import collections.abc as _cabc
import typing as _typing
from collections.abc import Callable
from typing import Any, Literal, Self, overload

from .._types import Types as _T  # noqa:N814
from ..empty import VOID, MayNot
from . import _zero as _z
from ._field import TupleField
from ._frozen import frozendict
from ._hashed import HashedTuple

type VarsView = _typing.Literal["live", "dict", "frozen"]


class KeyFormatting(_typing.Protocol):
    def __call__(self, target: object, /) -> str:
        """Render the Value to a valid Key"""


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class TupleControl(_z.TupleBase):
    """Inject Behaviour into NamedTuples"""

    __iter__: Any
    icon = TupleField[str]("◈")
    sep = TupleField[str](", ")

    def __str__(self) -> str:
        return self.__format__("")

    def __format__(self, spec: str, /) -> str:
        return _z.tuple_format(self, spec)

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Self:
        """
        Universal smart factory for any TupleControl NamedTuple.

        Supports:
          - None fallback to empty defaults / child .create()
          - Auto-coercion of raw Sequences/Mappings into child TupleControl types
          - Flattened prefix kwargs (e.g. text_args=..., error_kwargs=...)
        """
        return _z.create(cls, *args, **kwargs)

    @property
    def joined(self) -> str:
        """Concat all items in joins (equivalent to f'{self:b}')."""
        return self.__format__("b")

    def joins(self) -> _cabc.Iterator:
        """Stream the visual representation joins (indepenent of __iter__)"""
        yield from self

    @classmethod
    def mix[T](cls, target: type[T], /) -> _T._NoIntersect[T, Self]:
        """Inject Behaviour into Named Tuples"""
        namespace: dict[str, Any] = {
            "__qualname__": target.__qualname__,
            "__module__": target.__module__,
            "__doc__": target.__doc__,
        }
        return type(target.__name__, (target, cls), namespace)  # ty:ignore

    def __reduce__(self) -> _T.Tuple:
        """Provide anchor for Pickling"""
        raw_fields: _T.Tuple = tuple(tuple.__iter__(self))  # ty:ignore
        if state := getattr(self, "__dict__", None):
            return type(self), raw_fields, state
        return type(self), raw_fields


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class NamedValue[T: Any = Any](_typing.NamedTuple):
    name: str
    value: T

    def __bool__(self) -> bool:
        return bool(self.value)

    def __format__(self, spec: str) -> str:
        return _z.format_named_value(self, spec)

    def __getitem__(self, key: str | int) -> T | str:  # ty: ignore
        """Hardcore Encode Default Behaviour plus Var()[name]=value access"""
        return _z.get_named_value_item(self, key)

    def keys(self) -> _cabc.KeysView[str]:
        return _cabc.KeysView({self.name: None})

    def hashed(self, strict: bool = True) -> HashedTuple:
        """Recursively Enforce Freeze and Hash (strict=False -> str(obj))"""
        return HashedTuple(*self, strict=strict)


class SingleTuple[T: Any = Any](_typing.NamedTuple):
    data: T

    @property
    def tuple(self):
        return _b.tuple(self.data)

    @property
    def list(self):
        return _b.list(self.data)

    @property
    def set(self):  # LATER: check for not hashable
        return _b.set(self.data)

    def __iter__(self) -> _cabc.Iterator:
        yield from self.data

    def __len__(self) -> int:  # ty:ignore
        return len(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __contains__(self, item: object) -> bool:
        return item in self.data


class Variadics(_typing.NamedTuple):
    args: Args
    kwargs: Kwargs


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@TupleControl.mix
class Var[T: Any = Any](NamedValue[T]):
    """Variable with Name and Value"""

    sep = TupleField[str]("=")

    def __call__(self, *args, **kwargs) -> Any:
        """Invoke the Value if callable or provide its Representation"""
        if callable(self.value):
            return self.value(*args, **kwargs)
        return f"Not Callable: {self}[{self.value!r}]"

    @classmethod
    def gettr(cls, target: object, name: str, /) -> Self:
        """Hit the Target with the Name to get the Attr"""
        return cls(name, value=getattr(target, name))


@TupleControl.mix
class Args[S: _cabc.Sequence = _T.Tuple](SingleTuple[S]):
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
                data: _T.Tuple = tuple(data)
        return tuple.__new__(cls, (data,))

    def __getitem__(self, index: int) -> Any:  # ty: ignore
        """Forward Index to inner Tuple"""
        return self.data[index]

    def __add__(self, other: Self | _cabc.Sequence) -> Self:
        match other:
            case _ if isinstance(other, type(self)):
                other_seq: _T.Seq = other.data
            case _ if _z.is_notext_sequence(other):
                other_seq: _T.Seq = other
            case _:
                return NotImplemented
        return type(self)((*self.data, *other_seq))

    def __radd__[Seq: _cabc.Sequence](self, other: Seq) -> Seq:
        return (
            _z.merge_into_sequence(other, self.data)
            if _z.is_notext_sequence(other)
            else NotImplemented
        )

    def keys(self):
        return _cabc.KeysView({i: None for i, _ in enumerate(self)})

    def kwargs(self) -> Kwargs:
        """Transform Sequential Args into Mapped Kwargs (unwrapping Vars & deduplicating keys)."""
        out: dict[str, Any] = {}
        for item in self.data:
            _name, _val = (
                item  # -> name, val | tuple dereference
                if isinstance(item, Var)
                else (self.keyformat(item), item)  # LATER: keyformat on Var
            )
            out[_z.unique(_name, out)] = _val
        return Kwargs(**out)

    if _typing.TYPE_CHECKING:

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


@TupleControl.mix
class Kwargs[M: _T.Map](SingleTuple[M]):
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
        _merged = _z.merge_into_mapping(self.data, other_map)
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
        return (
            _z.merge_into_mapping(other, self.data)
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

    def __getitem__(self, key: str | int) -> Any:  # ty: ignore
        if isinstance(key, int):
            return self[tuple(self.keys())[key]]
        return self.data[key]

    def keys(self) -> _cabc.KeysView[str]:
        return self.data.keys()

    def args(self) -> Args:
        """Transform Mapped Kwargs into Sequential Args of Vars."""
        return Args(tuple(self))

    if _typing.TYPE_CHECKING:

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


@TupleControl.mix
class Params(Variadics):
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
            args = Args(args)
        if not isinstance(kwargs, Kwargs):
            kwargs = Kwargs(kwargs)
        return tuple.__new__(cls, (args, kwargs))

    def __or__(self, other: Params | Kwargs[Any] | _T.StrMap, /) -> Self:
        """Merge two Params (concatenating args and updating kwargs)."""
        if isinstance(other, Params):
            return type(self)(
                self.args + other.args, self.kwargs | other.kwargs
            )
        if isinstance(other, (Kwargs, _cabc.Mapping)):
            return type(self)(self.args, self.kwargs | other)
        return NotImplemented

    def __add__(self, other: Args[Any] | _cabc.Sequence[Any], /) -> Self:
        if _z.is_notext_sequence(other):
            return type(self)(self.args + other, self.kwargs)
        return NotImplemented

    def __sub__(self, other: _KeyFilter, /) -> Self:
        if isinstance(other, (Kwargs, _cabc.Set, _cabc.Mapping)):
            return type(self)(self.args, self.kwargs - other)
        return NotImplemented

    def __rmatmul__[R](self, func: Callable[..., R], /) -> R:
        return self.feed(func) if callable(func) else NotImplemented

    def __str__(self):
        return f"{type(self).__name__}[{self.args}{self.sep}{self.kwargs}]"

    def __bool__(self) -> bool:
        return bool(self.args) or bool(self.kwargs)

    def __iter__(self) -> _cabc.Iterator[Any]:
        yield from self.args

    def __getitem__(self, key: str) -> Any:  # ty: ignore
        return self.kwargs[key]

    def keys(self) -> _cabc.KeysView[str]:
        return self.kwargs.keys()

    def joins(self) -> _cabc.Iterator:  # TEST:
        yield from self.args
        yield from self.kwargs

    def feed[R](self, func: Callable[..., R], /) -> R:
        """Apply captured *args,**kwargs to Function"""
        return func(*self, **self)

    if _typing.TYPE_CHECKING:

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
