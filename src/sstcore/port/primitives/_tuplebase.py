"""
Tuple Features

-
"""

__all__: list[str] = [
    "TupleField",
    "TupleBase",
    "is_tuplebase_cls",
    "is_tuplebased",
    # tuple methods
    "merge_into_mapping",
    "merge_into_sequence",
    "get_named_value_item",
]

import collections.abc as _cabc
import inspect as _inspect
import typing as _typing
from collections.abc import Callable
from functools import cache
from types import NotImplementedType
from typing import Any, NamedTuple, Protocol, Self, overload

from .._types import Types as _T  # noqa:N814
from ..empty import VOID
from . import _zero as _z
from ._format import _TupleFormat, tuple_format


class TupleField[Value](_z.UnitField[Value]):
    """
    Generate Non-Member Field for (Named)Tuple with mutable values

    Assign WITHOUT type hint, like:
      - sep = TupleField[str]("=")
      - otherwise the Field is included as tuple member!
    """

    def __set__(self, unit: object, value: Value) -> None:
        """Update the per Instance Cache with the Value"""
        if hasattr(unit, "__dict__"):  # CHECK: mount to UnitField?
            super().__set__(unit, value)
            return
        raise TypeError(f"Missing {self}.__dict__: per unit cache not possible")


def is_tuplebased(target: object, /) -> _typing.TypeIs[TupleBase]:
    return isinstance(target, TupleBase)


def is_tuplebase_cls(target: object, /) -> _typing.TypeIs[type[TupleBase]]:
    _origin = _z.unpack_types(target)  # WARN: hashable?
    return isinstance(_origin, type) and issubclass(_origin, TupleBase)


class TupleBase(_TupleFormat):
    """Inject Behaviour into NamedTuples"""

    __iter__: Any
    icon = TupleField[str]("◈")
    sep = TupleField[str](", ")

    @property
    def joined(self) -> str:
        """Concat all items in joins (equivalent to f'{self:b}')."""
        return self.__format__("b")

    def joins(self) -> _cabc.Iterator:
        """Stream the visual representation joins (indepenent of __iter__)"""
        yield from self

    def __str__(self) -> str:
        return self.__format__("")

    def __format__(self, spec: str, /) -> str:
        return tuple_format(self, spec)

    def __reduce__(
        self,
    ) -> tuple[type, _T.Tuple] | tuple[type, _T.Tuple, _T.StrDict]:
        """Provide anchor for Pickling"""
        raw_fields: _T.Tuple = tuple(tuple.__iter__(self))  # ty:ignore
        if state := getattr(self, "__dict__", None):
            return type(self), raw_fields, state
        return type(self), raw_fields

    @classmethod
    def mix[T](cls, target: type[T], /) -> _T._NoIntersect[T, Self]:
        """Inject Behaviour into Named Tuples"""
        namespace: dict[str, Any] = {
            "__qualname__": target.__qualname__,
            "__module__": target.__module__,
            "__doc__": target.__doc__,
        }
        return type(target.__name__, (target, cls), namespace)  # ty:ignore

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Self:
        """
        Universal smart factory for any TupleBase NamedTuple.

        Supports:
          - None fallback to empty defaults / child .create()
          - Auto-coercion of raw Sequences/Mappings into child TupleBase types
          - Flattened prefix kwargs (e.g. text_args=..., error_kwargs=...)

        """
        if len(args) == 1 and not kwargs and isinstance(args[0], cls):
            return args[0]

        _fields, _defaults, _annotations = _tuple_schema(cls)

        if (n_a := len(args)) > (n_f := len(_fields)):
            raise TypeError(f"{_fn(cls)} Got {n_a} *args but takes max: {n_f}")

        _tasks = _TupleInputTasks.prepare(_fields, args, kwargs)
        _resolver = _tasks.create_field_resolver(cls, _defaults, _annotations)

        resolved: list[Any | VOID] = [_resolver(f) for f in _fields]

        _missing = [f for f, v in zip(_fields, resolved) if v is VOID]  # noqa:B905
        if _missing or _tasks.pending:
            raise TypeError(f"{_fn(cls)} failed! {_missing=} [{_tasks}]")

        return cls(*resolved)


def _fn(cls) -> str:
    return f" {cls.__name__}.create()"


class _TupleInputTasks(NamedTuple):
    """Helper: Define the Rules for the Resolving"""

    bound: _T.StrDict
    pending: _T.StrDict

    def __str__(self):
        return f"pending kwargs: {self.pending} (processed: {self.bound})"

    @classmethod
    def prepare(
        cls, fields: _T.StrTuple, args: _T.Tuple, kwargs: _T.Dict
    ) -> Self:
        """Compare Fields with inputs and assign values to process"""
        return cls(
            bound=(bound := dict(zip(fields, args, strict=False))),
            pending=_extract_kwargs(fields, bound, kwargs),
        )

    def create_field_resolver(
        self, cls: type, defaults: _T.StrDict, annotations: _T.StrDict
    ) -> Callable[[str], Any]:
        """Bind Resolver to process Field by Field"""

        def resolve(field: str) -> Any:
            """Extract recursively or return VOID on Fail"""
            field_type: object = annotations.get(field)
            field_value: object = self.bound.get(field)

            if is_tuplebase_cls(field_type):
                if field_value is not None:
                    return field_type.create(field_value)
                if prefixed := _extract_prefix(field, self.pending):
                    return field_type.create(**prefixed)
                return field_type.create()

            if field_value is not None:
                return field_value
            if field in defaults:
                return defaults[field]
            return VOID

        return resolve


def _extract_prefix(field, pending: _T.StrDict, /) -> _T.StrDict:
    return {
        k.removeprefix(prefix): pending.pop(k)
        for k in list(pending)
        if k.startswith(prefix := f"{field}_")  # PARAM: prefix format
    }


def _extract_kwargs(fields: _T.StrTuple, bound: _T.StrDict, kwargs: _T.StrDict):
    """Extract and Match kwargs and mutate Bound In-Place"""
    pending: _T.StrDict = {}
    for field_name, field_value in kwargs.items():
        if field_name in fields:
            pending[field_name] = field_value
        else:
            if field_name in bound:
                raise TypeError(f"Got multiple values for field {field_name!r}")
            bound[field_name] = field_value
    return pending


@cache
def _tuple_schema(cls: type[TupleBase]) -> _TupleSchema:
    """Scan Custom Tuple.__new__ and provide Fields, Defaults and Annotations"""

    fields: tuple[str, ...] = getattr(cls, "_fields", ())
    defaults: dict[str, Any] = dict(getattr(cls, "_field_defaults", {}))
    sig: _inspect.Signature = _inspect.signature(cls.__new__)
    params: list[_inspect.Parameter] = list(sig.parameters.values())[1:]

    for field, param in zip(fields, params, strict=False):
        if (
            field not in defaults
            and param.default is not _inspect.Parameter.empty
        ):
            defaults[field] = param.default

    return _TupleSchema(fields, defaults, _typing.get_type_hints(cls))


class _TupleSchema(NamedTuple):
    """Helper: Define the Order of the Annotation"""

    fields: _T.StrTuple
    defaults: _T.StrDict
    annotations: _T.StrDict


#  LINE: -- Attach to Cls -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _FromMapping(Protocol):
    def __init__(self, data: _T.Map, /) -> None: ...


class _FromIterable(Protocol):
    def __init__(self, data: _T.Seq, /) -> None: ...


@overload
def merge_into_mapping[K, V](
    target: dict[K, V], extra: _T.Map
) -> dict[K | Any, V | Any]: ...
@overload
def merge_into_mapping[M: _T.Map](
    target: M, extra: _T.Map
) -> M | NotImplementedType: ...
def merge_into_mapping(target: _T.Map, extra: _T.Map, /) -> Any:
    """Apply {Target | Extra} to type of target with overwrites from extra"""

    if (cls := type(target)) is dict:
        return {**target, **extra}

    _payload = extra if type(extra) is dict else dict(extra)

    if (lhs_or := getattr(cls, "__or__", None)) is not None:
        _result = lhs_or(target, _payload)
        if _result is not NotImplemented and type(_result) is cls:
            return _result
    try:
        return cls({**target, **extra})  # ty:ignore
    except TypeError:
        return NotImplemented


@overload
def merge_into_sequence[T](
    target: tuple[T, ...], extra: _T.Seq
) -> tuple[T | Any, ...]: ...
@overload
def merge_into_sequence[T](target: list[T], extra: _T.Seq) -> list[T | Any]: ...
@overload
def merge_into_sequence[Seq: _T.Seq](
    target: Seq, extra: _T.Seq
) -> Seq | NotImplementedType: ...
def merge_into_sequence(target: _T.Seq, extra: _T.Seq, /) -> Any:
    """Apply [Target + Extra] to type of target with overwrites from extra"""

    if (cls := type(target)) is tuple:
        return (*target, *extra)  # ty:ignor
    if cls is list:
        return [*target, *extra]  # ty:ignor
    if issubclass(cls, (str, bytes, bytearray)):
        return NotImplemented

    if (lhs_add := getattr(cls, "__add__", None)) is not None:
        try:
            _payload = cls(extra)  # ty:ignore
        except TypeError:
            _payload = extra
        _result = lhs_add(target, _payload)
        if _result is not NotImplemented and type(_result) is cls:
            return _result

    try:
        return cls((*target, *extra))  # ty:ignore
    except TypeError:
        return NotImplemented


def get_named_value_item[T](self, key: str | int) -> T | str:
    """Hardcore Encode Default Behaviour plus Var()[name]=value access"""
    if _typing.TYPE_CHECKING:
        key: Any = key
    match key:
        case int() as index if index == 0:
            return self.name
        case int() as index if index == 1:
            return self.value
        case int() as index:
            raise IndexError(f"{self} got {index=} but needs [0, 1]")
        case str() if key != (name := self.name):
            raise KeyError(f"{self} got {key=} but needs {name=}")
        case str():
            return self.value
        case _:
            raise TypeError(f"{self}: Unknown {type(key)}[{key=}]")
