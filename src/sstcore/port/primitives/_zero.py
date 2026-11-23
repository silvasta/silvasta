"""
Utils

-
"""

__all__: list[str] = [
    "portlink1",
    "unpack_types",
    "get_slots",
    "iter_slot_names",
    # tuple features
    "TupleBase",
    "is_tuplebase_cls",
    "is_tuplebase",
    "is_notext_sequence",
    "create",
    "merge_into_mapping",
    "merge_into_sequence",
    "get_named_value_item",
    # formatting
    "unique",
    "stringed",
    "tuple_format",
    "format_named_value",
    # views
    "NameView",
    "LoaderView",
]

import collections.abc as _cabc
import inspect as _inspect
import typing as _typing
from collections.abc import Callable
from functools import cache
from types import NotImplementedType, UnionType
from typing import Any, ClassVar, Union

from .._types import Types as _T  # noqa:N814
from ..empty import VOID, Ghost

_VALID_FLAGS: frozenset[str] = frozenset("bivn")
_EXPLAIN_FLAGS: frozenset[str] = frozenset("bivnte")


def portlink1[C, P](_protocol: type[P], /) -> Callable[[type[C & P]], type[C]]:  # ty:ignore
    """Anchor an Implementation to its Protocol - How everything began..."""

    def wrapper(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)
        """Accept class C iff C implements P and return C unchanged"""

        return cls

    return wrapper


@cache
def unpack_types(target: object, /) -> _T.Tuple[type]:
    """Flatten TypeAliases or UnionTypes into runtime-checkable Classes"""

    if isinstance(target, _typing.TypeAliasType):
        return unpack_types(target.__value__)

    if isinstance(target, UnionType) or _typing.get_origin(target) is Union:
        return tuple(
            cls
            for member in _typing.get_args(target)
            for cls in unpack_types(member)
        )

    if isinstance(resolved := _typing.get_origin(target) or target, type):
        return (resolved,)

    raise TypeError(f"Cannot unpack runtime type from {target!r}")


def get_slots(cls: type) -> _cabc.Iterable[str]:
    _slots = cls.__dict__.get("__slots__", ())
    return _slots if not isinstance(_slots, str) else (_slots,)


def iter_slot_names(target: object) -> _cabc.Iterable[str]:
    seen: set[str] = set()
    for cls in type(target).__mro__:
        for slot in get_slots(cls):
            if slot in ("__dict__", "__weakref__"):
                continue
            if slot.startswith("__") and not slot.endswith("__"):
                slot = f"_{cls.__name__.lstrip('_')}{slot}"
            if slot not in seen and hasattr(target, slot):
                seen.add(slot)
                yield slot


#  LINE: -- Tuple Features -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class TupleBase:
    """Define NameSpace for Custom NamedTuples"""


def is_tuplebase_cls(target: object, /) -> _typing.TypeIs[type[TupleBase]]:
    _origin = _typing.get_origin(target) or target
    return isinstance(_origin, type) and issubclass(_origin, TupleBase)


def is_tuplebase(target: object, /) -> _typing.TypeIs[TupleBase]:
    return isinstance(target, TupleBase)


def is_notext_sequence(target: object, /) -> bool:
    # LATER: any idea how to subtract StrLike from Sequence in TypeGuard?
    return isinstance(target, _cabc.Sequence) and not (
        isinstance(target, (str, bytes, bytearray))
    )


def unique(name: str, out: _T.StrDict):
    """Increment Dict Key Suffix until it is unique"""
    key: str = name
    counter = 1
    while key in out:
        key = f"{name}_{counter}"
        counter += 1
    return key


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


#  LINE: -- Format -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def stringed(val: object, /, *, verbose: bool = False) -> str:
    """Format values cleanly (types and functions by name unless verbose)"""
    if verbose:
        return repr(val)
    if isinstance(val, type):
        return val.__name__
    if callable(val) and hasattr(val, "__name__"):
        return getattr(val, "__qualname__", getattr(val, "__name__", repr(val)))
    return str(val)


def tuple_format(self, spec: str, /) -> str:
    """
    Composable Format Mini-Language:

      'b' : bare (only joined content, no ClassName[icon|...] wrapper)
      'i' : icon-only wrapper ([icon|...] without ClassName)
      'v' : verbose (preserve child ClassName wrappers & raw reprs)
      'n' : newline separated (multiline pretty output)
      ';X': use 'X' as custom separator (e.g., f"{obj:b; | }")

    """
    parsed: _SpecParse = _SpecParse.read(spec)
    body: str = parsed.active_sep(fallback=self.sep).join(
        _format_child(x, parsed.child_spec) for x in self.joins()
    )
    if parsed.multiline and body:
        indented: str = "\n".join(f"  {line}" for line in body.splitlines())
        body = f"\n{indented}\n"

    return body if parsed.bare else _format_box(self, parsed.icon_only, body)


def _format_child(child: object, child_spec: str, /) -> str:
    if isinstance(child, TupleBase):
        return child.__format__(child_spec)
    return stringed(child, verbose="v" in child_spec)


def is_explain_spec(spec: str, /) -> bool:
    """Check if a format_spec targets ExplainTuple rendering (t, e, v, n, i, ;sep)"""
    if not spec:
        return False
    flags, has_sep, _ = spec.partition(";")
    return bool(flags or has_sep) and set(flags) <= (_EXPLAIN_FLAGS - {"b"})


class _SpecParse(_typing.NamedTuple):
    bare: bool
    icon_only: bool
    verbose: bool
    multiline: bool
    title_only: bool = False
    explain_only: bool = False
    separator: str | None = None

    def active_sep(self, fallback: str) -> str:
        if self.separator is not None:
            return self.separator
        return "\n" if self.multiline else fallback

    @property
    def child_spec(self) -> str:
        base: str = "v" if self.verbose else "b"
        return f"{base}n" if self.multiline else base

    @classmethod
    def read(
        cls,
        spec: str,
        /,
        *,
        valid: frozenset[str] = _VALID_FLAGS,
    ) -> _SpecParse:
        """Parse Format Spec against allowed flag set."""
        _flags, _has_sep, _sep = spec.partition(";")
        if unknown := set(_flags) - valid:
            raise ValueError(
                f"Unknown format flag(s): {''.join(sorted(unknown))!r}"
            )
        return cls(
            bare="b" in _flags,
            icon_only="i" in _flags,
            verbose="v" in _flags,
            multiline="n" in _flags,
            title_only="t" in _flags,
            explain_only="e" in _flags,
            separator=_sep if _has_sep else None,
        )


def _split_spec(spec) -> tuple[str, str]:
    return (
        (spec.split(";", 1) + [""])[:2]  #
        if ";" in spec
        else (spec, "")
    )


def _collapse_or_multiline(
    text: str, *, multiline: bool, sep: str = " | "
) -> str:
    """Collapse multiline composite text into single-line unless multiline (:n) is active."""
    if multiline or "\n" not in text:
        return text
    return sep.join(line.strip() for line in text.splitlines() if line.strip())


def _format_box(self, icon_only: bool, body: str) -> str:
    prefix: str = f"{self.icon} | " if self.icon else ""
    header: str = "" if icon_only else type(self).__name__
    return f"{header}[{prefix}{body}]"


def format_named_value(self, spec: str) -> str:
    """Reduced Setup for NamedValue / Var"""
    parsed: _SpecParse = _SpecParse.read(spec)
    val_str: str = stringed(self.value, verbose=parsed.verbose)
    body = f"{self.name}{self.sep}{val_str}"
    return (
        body
        if parsed.bare and not parsed.verbose
        else _format_box(self, parsed.icon_only, body)
    )


def _rich_colorize(target, color="bold cyan", /):
    return f"[{color}]{target}[/]" if color else target


def format_explain(self: Any, spec: str, /) -> str:
    """
    Composable Format Mini-Language for ExplainTuple:

      '' / 't' : title (collapsed to single-line unless 'n' is set)
      'e'      : extended detail only
      'v'      : verbose (title + detail)
      'n'      : multiline output (title followed by indented detail)
      'i'      : wrap in icon box ([ⓘ | ...])
      'b'      : bare (unboxed, also compatible with TupleControl child_spec)
      ';X'     : custom separator between parts
    """
    parsed: _SpecParse = _SpecParse.read(spec, valid=_EXPLAIN_FLAGS)
    line_sep: str = parsed.separator or " | "

    title: str = _collapse_or_multiline(
        self.title, multiline=parsed.multiline, sep=line_sep
    )
    detail: str = _collapse_or_multiline(
        self.detail, multiline=parsed.multiline, sep=line_sep
    )

    include_both: bool = (
        (parsed.verbose or (parsed.multiline and not parsed.title_only))
        and not parsed.explain_only
    ) or (parsed.title_only and parsed.explain_only)

    if parsed.explain_only and not parsed.title_only:
        body: str = detail
    elif include_both and detail:
        if parsed.multiline:
            indented: str = "\n".join(
                f"  {line}" for line in self.detail.splitlines()
            )
            body = f"{title}\n{indented}"
        else:
            sep: str = parsed.active_sep(fallback=getattr(self, "sep", " — "))
            body = f"{title}{sep}{detail}"
    else:
        body = title

    if parsed.icon_only:
        if parsed.multiline and body:
            indented_box = "\n".join(f"  {line}" for line in body.splitlines())
            body = f"\n{indented_box}\n"
        return _format_box(self, icon_only=True, body=body)

    return body


_c = _rich_colorize


#  LINE: -- Views -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class NameView:
    pattern: str
    keys: _T.Tuple[str]

    _color: ClassVar[str] = "cyan"

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, color: str, /) -> None:
        type(self)._color = color

    @property
    def _short(self) -> str:
        return f"{len(self.keys)}:"

    def __str__(self):
        return f"{type(self).__name__}[{self._short}]"

    def __repr__(self):
        _name = s[0:-1] if (s := f"{self}").endswith("]") else ""
        _keys = ", ".join(self.keys)
        return f"{_name} | '{self.pattern}' -> {{{_keys}}}]"

    def __rich__(self):
        """Final goal: all keys in pattern same color as extracted"""
        _name = _rich_colorize(type(self).__name__, self.color)
        _keys = ", ".join(_rich_colorize(k, self.color) for k in self.keys)
        return f"{_name}[{self._short} | '{self.pattern}' -> {{{_keys}}}]"


if _typing.TYPE_CHECKING:
    from ._loader import Loader

    _LoaderViewBase = Loader
else:

    class _LoaderViewBase(Ghost): ...


class _LoaderView(_LoaderViewBase):
    _color: ClassVar[str] = "b steel_blue1"

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, color: str, /) -> None:
        type(self)._color = color

    def __str__(self) -> str:
        name: str = type(self).__name__
        is_ready: str = "👍️" if self.is_ready else "👎️"
        _in, _out = self.type_args.sig()
        _typearg = f"{_in} -> {_out}"
        _source = self.type_args.parameters_source
        return f"{name}[{is_ready}({self._value}) | {_typearg} via {_source}]"

    def __repr__(self) -> str:
        _d = {
            "func": getattr(self._func, "__name__", repr(self._func)),
            "default": repr(self._default),
            "prefer": self._prefer,
            "counter": f"{self._counter}/{self._total_counter}",
            "type_args": self.type_args,
        }
        return f"{self}({', '.join(f'{k}={v}' for k, v in _d.items())})"

    def __rich__(self) -> str:
        _orange = "orange_red1"
        _name = _c(type(self).__name__, self.color)
        _is_ready = _c("👍️", "green") if self.is_ready else _c("👎️", _orange)
        _value = _c(self._value, _orange if self._value is VOID else "cyan")
        _in, _out = self.type_args.sig()
        _typearg = f"{_c(_in, 'steel_blue1')} -> {_c(_out, 'green')}"
        _source = _c(self.type_args.parameters_source, "steel_blue1")
        return f"{_name}[{_is_ready}({_value}) | {_typearg} via {_source}]"


if _typing.TYPE_CHECKING:

    class LoaderView: ...
else:
    LoaderView = _LoaderView
