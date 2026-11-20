"""
Generic Type Arg - Extractor

Read runtime type args from:
  - __orig_class__
  - __orig_bases__
  - __type_params__
  ..then substitutes TypeVars down the MRO.

Todo:
- ParamSpec arguments are flattened in GenericAlias.__args__
- They are aligned back onto __type_params__ here
- One variadic parameter is unambiguous
- two are not, and that spec is marked unaligned

"""

__all__: list[str] = [
    "GenericSpec",
    "extract_type_args",
    "format_type_arg",
    "is_concrete_type",
    "is_type_parameter",
    "normalize_orig_bases",
    "preserves_generic_alias_on_instance",
    "remembering_getitem",
]

import operator
import weakref
from collections.abc import Iterator, Mapping
from contextlib import suppress
from dataclasses import dataclass
from functools import reduce
from types import GenericAlias, UnionType, get_original_bases
from typing import (
    Any,
    Concatenate,
    Generic,
    NamedTuple,
    ParamSpec,
    Protocol,
    Self,
    TypeVar,
    TypeVarTuple,
    get_args,
    get_origin,
)

from ..empty import VOID, MayBe, MayNot

_TYPE_PARAMS = (TypeVar, ParamSpec, TypeVarTuple)
_IGNORED_ORIGINS = frozenset({Generic, Protocol})
_STAMPS: weakref.WeakKeyDictionary[Any, Any] = weakref.WeakKeyDictionary()


def extract_type_args(target: Any) -> tuple[GenericSpec, ...]:
    """Every specialization visible on ``target``, most specific first.

    Accepts an instance, a class, or a generic alias. Parent aliases are
    included, with type variables substituted from more specific bases.
    An unspecialized generic class contributes one implicit spec whose
    arguments are its own parameters.
    """
    data = _ExtractDTO(env={}, specs=[], seen=set())

    if _is_alias_object(target):
        _consume(target, *data)
        if (parts := _alias_parts(target)) and isinstance(parts.origin, type):
            _walk_bases(parts.origin, *data)
        return tuple(data.specs)

    if not isinstance(target, type):
        if (orig := _orig_class_of(target)) is not None:
            _consume(orig, *data)

    cls: type = target if isinstance(target, type) else type(target)

    _walk_bases(cls, *data)
    _add_identity(cls, data)

    return tuple(data.specs)


class _ExtractDTO(NamedTuple):
    env: dict[Any, Any]
    specs: list[GenericSpec]
    seen: set[Any]

    def record(self, spec: GenericSpec, /) -> None:  # LATER: use this!
        self.specs.append(spec)
        self.seen.add(spec.origin)


@dataclass(frozen=True, slots=True)
class GenericSpec:
    """One origin and its arguments, already substituted from subclasses.

    ``explicit`` is False for the synthetic identity spec built from a
    class's own ``__type_params__``. That spec means "not specialized",
    not "the user wrote this".
    """

    origin: Any
    parameters: tuple[Any, ...]
    arguments: tuple[Any, ...]
    aligned: bool
    explicit: bool

    def get(self, name: str, default: Any = VOID) -> Any:
        if not self.aligned or len(self.parameters) != len(self.arguments):
            return default
        for param, arg in zip(self.parameters, self.arguments, strict=True):
            if getattr(param, "__name__", None) == name:
                return arg
        return default

    def __str__(self) -> str:
        _origin = getattr(self.origin, "__qualname__", f"{self.origin}")
        if not self.aligned:
            _body = ", ".join(format_type_arg(arg) for arg in self.arguments)
            return f"{_origin}[{_body}]?"
        parts: list[str] = [
            format_parameters(arg)
            if isinstance(param, ParamSpec)
            else format_type_arg(arg)
            for param, arg in zip(self.parameters, self.arguments, strict=True)
        ]
        return f"{_origin}[{', '.join(parts)}]"

    def is_to_declare(self, origin: type) -> bool:
        return self.explicit and self.aligned and self.origin is origin


def format_type_arg(arg: Any, /) -> str:
    """Short display form. Not a round-trippable signature."""
    if arg is VOID:
        return "VOID"
    if arg is Ellipsis:
        return "..."
    if arg is None:
        return "None"
    if isinstance(arg, tuple):
        return "(" + ", ".join(format_type_arg(item) for item in arg) + ")"
    if isinstance(arg, type):
        return arg.__qualname__
    if is_type_parameter(arg):
        return getattr(arg, "__name__", f"{arg}")
    if isinstance(name := getattr(arg, "__name__", None), str):
        return name
    return str(arg).removeprefix("typing.")


def format_parameters(arg: Any, /) -> str:
    """ParamSpec slot. ``(...)`` is unspecified, ``()`` is an empty list.

    ``format_type_arg(Ellipsis)`` is only ``...``. Using it here erases
    that difference, so this is a second rule, not a second copy.
    """
    if arg is VOID or arg is Ellipsis:
        return "(...)"
    if isinstance(arg, tuple):
        return "(" + ", ".join(format_type_arg(item) for item in arg) + ")"
    return format_type_arg(arg)


def is_type_parameter(target: Any, /) -> bool:
    """True for a bare TypeVar, ParamSpec, or TypeVarTuple."""
    return isinstance(target, _TYPE_PARAMS)


def is_concrete_type(target: Any, /) -> bool:
    """True when target can be used as a resolved type, not an open parameter.

    Ellipsis is a specified ParamSpec token, not a value type, so it is
    not concrete. Tuples are concrete only when every element is.
    """
    if target is VOID or target is Ellipsis or is_type_parameter(target):
        return False
    if isinstance(target, tuple):
        return all(is_concrete_type(item) for item in target)
    return True


def normalize_orig_bases(cls: type) -> None:
    """Rewrite remembering aliases in ``__orig_bases__`` to ``GenericAlias``."""
    if not (bases := getattr(cls, "__orig_bases__", None)):
        return
    if bases == (normalized := tuple(_coerce_alias(base) for base in bases)):
        return
    with suppress(AttributeError, TypeError):
        cls.__orig_bases__ = normalized  # ty:ignore


def preserves_generic_alias_on_instance() -> bool:
    """Whether ``Cls[Arg]()`` keeps the alias on ``__orig_class__``."""
    return _PRESERVES_ALIAS


def remembering_getitem(origin: type, /, params: Any) -> Any:
    """``__class_getitem__`` result that survives instantiation and subclassing.

    Only needed when ``preserves_generic_alias_on_instance()`` is false.
    The object is a real base via ``__mro_entries__``. Call
    ``normalize_orig_bases`` from ``__init_subclass__`` so the stored base
    becomes a normal ``GenericAlias`` and ``get_args`` can see it.
    """
    return _RememberingAlias(origin, params)


def _probe_preserves_alias() -> bool:
    class _Probe[T]: ...

    try:
        instance = _Probe[int]()
    except TypeError:
        return False
    return getattr(instance, "__orig_class__", None) is not None


_PRESERVES_ALIAS = _probe_preserves_alias()


class _RememberingAlias:
    __slots__ = ("__origin__", "__args__", "_generic_alias")

    def __init__(self, origin: type, params: Any) -> None:
        _raw = params if isinstance(params, tuple) else (params,)
        alias = GenericAlias(origin, _raw)
        self.__origin__ = origin
        self.__args__ = get_args(alias)
        self._generic_alias = alias

    def __mro_entries__(self, bases: tuple[Any, ...]) -> tuple[type, ...]:
        return (self.__origin__,)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        target = self.__origin__(*args, **kwargs)
        _attach_orig_class(target, self._generic_alias)
        return target

    def __repr__(self) -> str:
        return repr(self._generic_alias)


def _coerce_alias(base: Any) -> Any:
    return getattr(base, "_generic_alias", base)


def _attach_orig_class(target: Any, alias: Any) -> None:
    try:
        target.__orig_class__ = alias
        return
    except AttributeError, TypeError:
        with suppress(TypeError):
            _STAMPS[target] = alias


def _orig_class_of(target: Any, /) -> Any:
    return (
        found
        if (found := getattr(target, "__orig_class__", None)) is not None
        else _STAMPS.get(target)
    )


def _is_alias_object(target: Any) -> bool:
    if target is None or isinstance(target, type):
        return False
    if isinstance(target, GenericAlias):
        return True
    parts: MayNot[_AliasParts] = _alias_parts(target)
    if parts is None or not isinstance(parts.origin, type):
        return False
    return not isinstance(target, parts.origin)


class _AliasParts(NamedTuple):
    origin: Any
    args: tuple[Any, ...]

    @classmethod
    def fetch(
        cls, target, origin: MayBe = VOID, args: MayBe[tuple[Any, ...]] = VOID
    ) -> Self:
        return cls(
            origin=get_origin(target) if origin is VOID else origin,
            args=get_args(target) if args is VOID else args,
        )

    @classmethod
    def gettr(cls, target) -> MayNot[Self]:
        if (origin := getattr(target, "__origin__", None)) is None:
            return None
        if not isinstance(args := getattr(target, "__args__", None), tuple):
            return None
        return cls(origin, args)


def _alias_parts(target: Any, /) -> _AliasParts | None:
    if target is None or isinstance(target, type):
        return None
    if isinstance(target, GenericAlias):
        return _AliasParts.fetch(target)
    if (origin := get_origin(target)) is not None:
        return _AliasParts.fetch(target, origin)
    if (alias_parts := _AliasParts.gettr(target)) is None:
        return None
    return alias_parts


def _is_paramspec_token(target: Any, /) -> bool:
    if target is Ellipsis or isinstance(target, ParamSpec):
        return True
    origin = get_origin(target)
    return (
        origin is Concatenate
        or getattr(origin, "__name__", None) == "Concatenate"
    )


def _walk_bases(
    cls: type,
    /,
    env: dict[Any, Any],
    specs: list[GenericSpec],
    seen: set[Any],
) -> None:
    for superclass in cls.__mro__:
        for base in _original_bases(superclass):
            _consume(base, env, specs, seen)


def _original_bases(cls: type, /) -> Iterator[Any]:
    with suppress(TypeError):
        yield from get_original_bases(cls)


def _consume(
    alias: Any,
    /,
    env: dict[Any, Any],
    specs: list[GenericSpec],
    seen: set[Any],
) -> None:
    if (  # LATER: basically validation of _AliasParts
        (parts := _alias_parts(alias)) is None
        or not isinstance(parts.origin, type)
        or parts.origin in _IGNORED_ORIGINS
        or parts.origin in seen
    ):
        return

    _substituted = tuple(_apply_subst(item, env) for item in parts.args)

    if (align_args := _align_args(parts.origin, _substituted)).ok:
        _extend_env(env, align_args.params, align_args.aligned)

    specs.append(
        GenericSpec(
            origin=parts.origin,
            parameters=align_args.params,
            arguments=align_args.aligned,
            aligned=align_args.ok,  # TASK: resolve naming confusion
            explicit=True,
        )
    )
    seen.add(parts.origin)


def _extend_env(
    env: dict[Any, Any], params: tuple[Any, ...], args: tuple[Any, ...], /
) -> None:
    for param, arg in zip(params, args, strict=True):
        if is_type_parameter(param) and param not in env:
            env[param] = arg


class _AlignArgs(NamedTuple):
    params: tuple[Any, ...]
    aligned: tuple[Any, ...]
    ok: bool


def _align_args(origin: Any, args: tuple[Any, ...], /) -> _AlignArgs:
    """Pair ``args`` with ``origin``'s parameters.

    A ParamSpec occupies one logical slot even when its list was flattened
    into ``__args__``. A single TypeVarTuple is handled the same way.
    """
    if not (params := _type_parameters(origin)):
        return _AlignArgs(params=(), aligned=args, ok=False)

    variadic: list[int] = [
        index
        for index, param in enumerate(params)
        # AI_QUESTION: what about TypeVar?
        # - otherwise just use: is_type_parameter
        if isinstance(param, (ParamSpec, TypeVarTuple))
    ]
    if len(variadic) != 1:
        return _AlignArgs(params, aligned=args, ok=len(args) == len(params))

    index = variadic[0]
    fixed_before = index
    fixed_after = len(params) - index - 1
    if len(args) < fixed_before + fixed_after:
        return _AlignArgs(params=(), aligned=args, ok=False)

    before: tuple[Any, ...] = args[:fixed_before]
    middle: tuple[Any, ...] = args[
        fixed_before : len(args) - fixed_after if fixed_after else len(args)
    ]
    after: tuple[Any, ...] = (
        args[len(args) - fixed_after :] if fixed_after else ()
    )
    if isinstance(_param := params[index], ParamSpec):
        if len(middle) == 1 and _is_paramspec_token(middle[0]):
            mid: Any = middle[0]
        elif len(middle) == 1 and isinstance(middle[0], (tuple, list)):
            mid: tuple[Any, ...] = tuple(middle[0])
        else:
            mid: tuple[Any, ...] = middle
    else:
        mid: tuple[Any, ...] = middle
    return _AlignArgs(params, aligned=before + (mid,) + after, ok=True)


def _type_parameters(origin: Any) -> tuple[Any, ...]:
    if params := getattr(origin, "__type_params__", ()):
        return tuple(params)
    return tuple(getattr(origin, "__parameters__", ()))


def _apply_subst(arg: Any, env: Mapping[Any, Any], /) -> Any:
    if not env:
        return arg
    if is_type_parameter(arg):
        return env.get(arg, arg)

    if isinstance(arg, tuple):
        return tuple(_apply_subst(x, env) for x in arg)
    if isinstance(arg, UnionType):
        return _rebuild_union(tuple(_apply_subst(x, env) for x in arg.__args__))

    if (origin := get_origin(arg)) is None or not (raw := get_args(arg)):
        return arg
    if (updated := tuple(_apply_subst(x, env) for x in raw)) == raw:
        return arg
    return _respecialize(origin, updated)


def _rebuild_union(parts: tuple[Any, ...], /) -> Any:
    return reduce(operator.or_, parts) if parts else VOID


def _respecialize(origin: Any, args: tuple[Any, ...]) -> Any:
    try:
        if len(args) == 1:
            return origin[args[0]]
        return origin[args]
    except TypeError:
        if isinstance(origin, type):
            return GenericAlias(origin, args)
        return args


def _add_identity(cls: type, data: _ExtractDTO) -> None:
    if cls in data.seen:
        return
    if not (params := tuple(getattr(cls, "__type_params__", ()))):
        return
    data.record(
        GenericSpec(
            origin=cls,
            parameters=params,
            arguments=params,
            aligned=True,
            explicit=False,
        )
    )
