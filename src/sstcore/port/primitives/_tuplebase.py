"""
Tuple Features

-
"""

__all__: list[str] = [
    "TupleBase",
    "TupleField",
    "is_tuplebase_cls",
    "is_tuplebased",
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
from typing import Any, NamedTuple, Self, overload

from .._types import Types as _T  # noqa:N814
from ..empty import VOID, MayBe, MayNot
from ._format import tuple_format


class TupleField[Value]:  # CHECK: Tuple? or more general?
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


#  LINE: -- Mountables for Classes -- -- - -- -- - -- -- - -- -- - -- -- - -- --


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


def merge_into_sequence[Seq: _T.Seq](
    target: Seq, extra: _T.Seq, /
) -> Seq | NotImplementedType:
    """Apply [Target + Extra] to type of target with overwrites from extra"""

    cls: type[Seq] = type(target)

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


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _TupleSchema(NamedTuple):
    """Helper: Define the Order of the Annotation"""

    fields: _T.StrTuple
    defaults: _T.StrDict
    annotations: _T.StrDict


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
            pending=_remaining_kwargs(fields, bound, kwargs),
        )

    def create_field_resolver(
        self, cls: type, defaults: _T.StrDict, annotations: _T.StrDict
    ) -> Callable[[str], Any]:
        """Bind Resolver that processes one Field by another"""

        def resolve(field: str) -> Any:

            _field_type = annotations.get(field)
            _prefixed = _extract_prefixed(f"{field}_", self.pending)

            if _prefixed and is_tuplebase_cls(_field_type):
                return _field_type.create(**_prefixed)

            if field in self.bound and (val := self.bound[field]) is not None:
                if is_tuplebase_cls(_field_type) and not isinstance(
                    val, _field_type
                ):
                    return _field_type.create(val)
                else:
                    return val

            if is_tuplebase_cls(_field_type):
                return _field_type.create()

            if field in defaults:
                return defaults[field]

            raise TypeError(
                f"{cls.__name__}.create() missing required field: {field!r}"
            )

        return resolve


def _remaining_kwargs(fields, bound, kwargs):
    remaining_kwargs: _T.StrDict = dict(kwargs)
    for field in fields:
        if field in remaining_kwargs:
            bound[field] = remaining_kwargs.pop(field)
    return remaining_kwargs


def _extract_prefixed(prefix, pending: _T.StrDict, /) -> _T.StrDict:
    """Destroy Kwargs if they match the Prefix"""
    return {
        # AI: unsure about this, when is what removed?
        k.removeprefix(prefix): pending.pop(k)
        for k in list(pending)
        if k.startswith(prefix)
    }


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def is_tuplebased(target: object, /) -> _typing.TypeIs[TupleBase]:
    return isinstance(target, TupleBase)


def is_tuplebase_cls(target: object, /) -> _typing.TypeIs[type[TupleBase]]:
    _origin = _typing.get_origin(target) or target
    return isinstance(_origin, type) and issubclass(_origin, TupleBase)


class TupleBase:
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

    def __reduce__(self) -> _T.Tuple:
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
        if from_empty := _check_empty(cls, args, kwargs):
            return from_empty  # REMOVE:??

        if _already_ready(cls, args, kwargs):
            return args[0]

        _fields, _defaults, _annotations = _tuple_schema(cls)

        _accept_or_raise_on_positional(cls, args, _fields)

        _tasks = _TupleInputTasks.prepare(_fields, args, kwargs)
        _resolve = _tasks.create_field_resolver(cls, _defaults, _annotations)
        resolved: list[Any] = [_resolve(field) for field in _fields]

        if _tasks.pending:
            raise TypeError(f"{cls.__name__}.create() Input Failed! [{_tasks}]")

        return cls(*resolved)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _check_empty(cls, args, kwargs):
    if not args and not kwargs:
        try:
            return cls()
        except TypeError:
            pass  # AI: can this ever recover afterwards?


def _already_ready(cls, args, kwargs) -> bool:
    """Catch Case where an already prepared instance is placed in a nested setup"""
    return len(args) == 1 and not kwargs and isinstance(args[0], cls)


def _accept_or_raise_on_positional(cls, args, fields):
    if len(args) > len(fields):
        raise TypeError(
            f"{cls.__name__}.create() takes at most {len(fields)} positional args, got {len(args)}"
        )
