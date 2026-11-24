"""
Tuple Features

-
"""

__all__: list[str] = [
    "TupleBase",
    "TupleField",
    "is_tuplebase_cls",
    "is_tuplebase",
    "create",
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
from typing import Any, Self, overload

from .._types import Types as _T  # noqa:N814
from ..empty import VOID, MayBe, MayNot
from ._format import tuple_format


class TupleField[Value]:  # CHECK: Tuple?
    """
    Generate Non-Member Field for (Named)Tuple with mutable values

    - Cache Data per Instance by using the unit.__dict__ as cache

    Assign WITHOUT type hint, like:
      - sep = TupleField[str]("=")
      - otherwise the Field is included as tuple member!

    """

    def __init__(self, default: MayBe[Value], /):
        self._default: MayBe[Value] = default

    def __set_name__(self, host: type, name: str) -> None:
        """Define the Name, Assigner:{initial owner} and Hoster:{last owner}"""
        self._name: str = name
        self._host: type = host
        self._caller: type = host

    def __call__[Fn: Callable](self, func: Fn) -> Fn:
        """Make a Method Exchangeable"""
        self._default: Fn = func
        return func

    def __str__(self):
        """Represent (HostCls::)Cls.field_name"""
        return f"{self._host.__name__}{self._scope}.{self._name}"

    @property
    def _scope(self) -> str:
        """Represent Host or Host::Caller"""
        return f"::{self._caller.__name__}" if self._inherited else ""

    @property
    def _inherited(self) -> bool:
        """Was the field last accessed through a subclass rather than its host?"""
        return self._host is not self._caller

    @overload
    def __get__(self, unit: None, caller: type) -> Self: ...
    @overload
    def __get__(self, unit: object, caller: type) -> Value: ...

    def __get__(self, unit: MayNot, caller: type) -> Self | Value:
        """Extract per Unit from Cache or try set Default"""
        # TEST: differences in the ids
        # print(f"Get: {self}")
        # print(f"{self._host=}\n{self._caller=}\n{self._inherited=}")
        # print(f"{id(self._host)=}\n{id(self._caller)=}\n{id(self._inherited)=}")
        self._caller: type = caller  # TODO: where to place this??
        return self if unit is None else self[unit]

    def __set__(self, unit: object, value: Value) -> None:
        """Update the per Instance Cache with the Value"""
        self[unit] = value

    def __getitem__(self, unit: object):
        if unit not in self:
            self[unit] = self._default
        return vars(unit)[self._name]

    def __setitem__(self, unit: object, value: Any):
        if value is VOID:
            raise RuntimeError(f"Assign Value or Default to Access: {self}")
        # NEXT: Validate (type of) Value, extract TypeArg?
        vars(unit)[self._name] = value

    def __contains__(self, target: object):
        """Heavily Wired! Change with care..."""
        return self._name in vars(target)

    def __delete__(self, unit: object) -> None:
        """Remove the Value of Unit from the Cache"""
        vars(unit).pop(self._name, None)


def is_tuplebase_cls(target: object, /) -> _typing.TypeIs[type[TupleBase]]:
    # RENAME:
    _origin = _typing.get_origin(target) or target
    return isinstance(_origin, type) and issubclass(_origin, TupleBase)


def is_tuplebase(target: object, /) -> _typing.TypeIs[TupleBase]:
    # RENAME:
    return isinstance(target, TupleBase)


@cache
def _tuple_schema(
    cls: type[TupleBase],
) -> tuple[tuple[str, ...], dict[str, Any], dict[str, Any]]:
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

    return fields, defaults, _typing.get_type_hints(cls)


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


def merge_into_sequence[S: _T.Seq](
    target: S, extra: _T.Seq, /
) -> S | NotImplementedType:
    """Apply [Target + Extra] to type of target with overwrites from extra"""

    cls: type[S] = type(target)

    if cls is tuple:
        return (*target, *extra)  # ty:ignore
    if cls is list:
        return [*target, *extra]  # ty:ignore
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


def create[C: TupleBase](cls: type[C], *args: Any, **kwargs: Any) -> C:
    """
    Universal smart factory for any TupleBase NamedTuple.

    Supports:
      - None fallback to empty defaults / child .create()
      - Auto-coercion of raw Sequences/Mappings into child TupleBase types
      - Flattened prefix kwargs (e.g. text_args=..., error_kwargs=...)

    """
    if not args and not kwargs:
        try:
            return cls()
        except TypeError:
            pass

    if len(args) == 1 and not kwargs and isinstance(args[0], cls):
        return args[0]

    _fields, _defaults, _annotations = _tuple_schema(cls)

    if len(args) > len(_fields):
        raise TypeError(
            f"{cls.__name__}.create() takes at most {len(_fields)} "
            f"positional args, got {len(args)}"
        )

    bound: _T.StrDict = dict(zip(_fields, args, strict=False))
    remaining: _T.StrDict = _remaining_kwargs(_fields, bound, kwargs)

    resolved: list[Any] = [
        _resolve_field(
            cls,
            field,
            _extract_prefixed(f"{field}_", remaining),
            bound,
            _defaults,
            field_type=_annotations.get(field),
        )
        for field in _fields
    ]
    if remaining:
        bad: str = ", ".join(repr(k) for k in remaining)
        raise TypeError(f"{cls.__name__}.create() unexpected kwargs: {bad}")

    return cls(*resolved)


def _resolve_field(cls, field, prefixed, bound, defaults, field_type):
    if prefixed and is_tuplebase_cls(field_type):
        return field_type.create(**prefixed)
    if field in bound and (val := bound[field]) is not None:
        if is_tuplebase_cls(field_type) and not isinstance(val, field_type):
            return field_type.create(val)
        else:
            return val
    if is_tuplebase_cls(field_type):
        return field_type.create()
    if field in defaults:
        return defaults[field]
    raise TypeError(
        f"{cls.__name__}.create() missing required field: {field!r}"
    )


def _extract_prefixed(prefix, to_pop: _T.StrDict, /) -> _T.StrDict:
    return {
        k.removeprefix(prefix): to_pop.pop(k)
        for k in list(to_pop)
        if k.startswith(prefix)
    }


def _annotations(cls) -> _T.StrDict:
    return (
        _typing.get_type_hints(cls)
        if hasattr(cls, "__annotations__")  # CHECK: needed?
        else {}
    )


def _remaining_kwargs(fields, bound, kwargs):
    remaining_kwargs: _T.StrDict = dict(kwargs)
    for field in fields:
        if field in remaining_kwargs:
            bound[field] = remaining_kwargs.pop(field)
    return remaining_kwargs


class TupleBase:
    """Inject Behaviour into NamedTuples"""

    __iter__: Any
    icon = TupleField[str]("◈")
    sep = TupleField[str](", ")

    def __str__(self) -> str:
        return self.__format__("")

    def __format__(self, spec: str, /) -> str:
        return tuple_format(self, spec)

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Self:
        """
        Universal smart factory for any TupleBase NamedTuple.

        Supports:
          - None fallback to empty defaults / child .create()
          - Auto-coercion of raw Sequences/Mappings into child TupleBase types
          - Flattened prefix kwargs (e.g. text_args=..., error_kwargs=...)
        """
        return create(cls, *args, **kwargs)

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
