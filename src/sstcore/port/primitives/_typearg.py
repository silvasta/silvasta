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

from contextlib import suppress
from functools import partial

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

import weakref
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from types import GenericAlias, UnionType, get_original_bases
from typing import (
    Any,
    Concatenate,
    Generic,
    ParamSpec,
    Protocol,
    TypeVar,
    TypeVarTuple,
    get_args,
    get_origin,
)

from ..empty import VOID

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
    env: dict[Any, Any] = {}  # LATER: make this 3 like some container
    specs: list[GenericSpec] = []
    seen: set[Any] = set()

    if _is_alias_object(target):
        _consume(target, env, specs, seen)
        _origin = _alias_parts(target)
        if _origin is not None and isinstance(_origin[0], type):
            _walk_bases(_origin[0], env, specs, seen)
        return tuple(specs)

    if not isinstance(target, type):
        if (orig := _orig_class_of(target)) is not None:
            _consume(orig, env, specs, seen)

    cls: type = target if isinstance(target, type) else type(target)

    _walk_bases(cls, env, specs, seen)
    _add_identity(cls, specs, seen)

    return tuple(specs)


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
        if not self.aligned:
            return default
        for param, arg in zip(self.parameters, self.arguments, strict=True):
            if getattr(param, "__name__", None) == name:
                return arg
        return default

    def __str__(self) -> str:
        _origin = getattr(self.origin, "__qualname__", f"{self.origin}")
        # AI: the aligned made like no difference, maybe UnTyped/VOID or (...) or ..., bettr collapse
        return f"{_origin}[{format_type_arg(self.arguments)}]?"

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
    except TypeError, Exception:
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
    _parts = _alias_parts(target)
    if _parts is None or not isinstance(_parts[0], type):
        return False
    return not isinstance(target, _parts[0])


def _alias_parts(target: Any, /) -> tuple[Any, tuple[Any, ...]] | None:
    if target is None or isinstance(target, type):
        return None
    if isinstance(target, GenericAlias):
        return get_origin(target), get_args(target)
    if (origin := get_origin(target)) is not None:
        return origin, get_args(target)
    _origin = getattr(target, "__origin__", None)
    _args = getattr(target, "__args__", None)
    if _origin is not None and isinstance(_args, tuple):
        return _origin, _args
    return None


def _is_paramspec_token(target: Any) -> bool:
    if target is Ellipsis or isinstance(target, ParamSpec):
        return True
    origin = get_origin(target)
    return (
        origin is Concatenate
        or getattr(origin, "__name__", None) == "Concatenate"
    )


def _walk_bases(
    cls: type,
    env: dict[Any, Any],
    specs: list[GenericSpec],
    seen: set[Any],
) -> None:
    for superclass in cls.__mro__:
        for base in _original_bases(superclass):
            _consume(base, env, specs, seen)


def _original_bases(cls: type, /) -> Iterator[type]:
    with suppress(TypeError):
        yield from get_original_bases(cls)


def _consume(
    alias: Any,
    /,
    env: dict[Any, Any],
    specs: list[GenericSpec],
    seen: set[Any],
) -> None:
    if (parts := _alias_parts(alias)) is None:
        return

    _origin, _raw_args = parts  # WARN: does this proper unpack?

    if not isinstance(_origin, type) or _ignored(_origin) or _origin in seen:
        return

    _substituted = _apply_subst_on_iter(_raw_args, env)
    _params, _aligned, _ok = _align_args(_origin, _substituted)
    if _ok:
        _extend_env(env, _params, _aligned)

    specs.append(
        GenericSpec(
            origin=_origin,
            parameters=_params,
            arguments=_aligned,
            aligned=_ok,
            explicit=True,
        )
    )
    seen.add(_origin)


def _ignored(origin: Any, /) -> bool:
    return origin in _IGNORED_ORIGINS


def _extend_env(
    env: dict[Any, Any], params: tuple[Any, ...], args: tuple[Any, ...]
) -> None:
    for param, arg in zip(params, args, strict=True):
        if is_type_parameter(param) and param not in env:
            env[param] = arg


def _align_args(
    origin: Any, args: tuple[Any, ...]
) -> tuple[tuple[Any, ...], tuple[Any, ...], bool]:
    """Pair ``args`` with ``origin``'s parameters.

    A ParamSpec occupies one logical slot even when its list was flattened
    into ``__args__``. A single TypeVarTuple is handled the same way.
    """
    if not (params := _type_parameters(origin)):
        return (), args, False

    variadic: list[int] = [
        index
        for index, param in enumerate(params)
        if isinstance(param, (ParamSpec, TypeVarTuple))
    ]
    if not variadic:
        return params, args, len(args) == len(params)
    if len(variadic) != 1:
        return params, args, len(args) == len(params)

    index = variadic[0]
    fixed_before = index
    fixed_after = len(params) - index - 1
    if len(args) < fixed_before + fixed_after:
        return params, args, False

    before = args[:fixed_before]
    after = args[len(args) - fixed_after :] if fixed_after else ()
    middle = args[
        fixed_before : len(args) - fixed_after if fixed_after else len(args)
    ]
    param = params[index]
    if isinstance(param, ParamSpec):
        mid: Any
        if len(middle) == 1 and _is_paramspec_token(middle[0]):
            mid = middle[0]
        elif len(middle) == 1 and isinstance(middle[0], (tuple, list)):
            mid = tuple(middle[0])
        else:
            mid = middle
    else:
        mid = middle
    return params, before + (mid,) + after, True


def _type_parameters(origin: Any) -> tuple[Any, ...]:
    if params := getattr(origin, "__type_params__", ()):
        return tuple(params)
    return tuple(getattr(origin, "__parameters__", ()))


def _apply_subst_on_iter(iterable: Iterable, /, env: Mapping):
    return tuple(_apply_subst(item, env) for item in iterable)


def _apply_subst(arg: Any, env: Mapping[Any, Any], /) -> Any:
    if not env:
        return arg
    if is_type_parameter(arg):
        return env.get(arg, arg)

    _apply_on_iter = partial(_apply_subst_on_iter, env=env)

    if isinstance(arg, tuple):
        return _apply_on_iter(arg)
    if isinstance(arg, UnionType):
        return _rebuild_union(_apply_on_iter(arg.__args__))

    if (origin := get_origin(arg)) is None:
        return arg
    if not (raw := get_args(arg)):
        return arg
    if (updated := (_apply_on_iter(raw))) == raw:
        return arg

    return _respecialize(origin, updated)


def _rebuild_union(parts: tuple[Any, ...], /) -> Any:
    if not parts:
        return VOID
    _current, *_maybe_following = parts
    for part in _maybe_following:
        # AI_QUESTION: is there like a comprehension for | ?
        _current = _current | part
    return _current


def _respecialize(origin: Any, args: tuple[Any, ...]) -> Any:
    try:
        if len(args) == 1:
            return origin[args[0]]
        return origin[args]
    except TypeError:
        if isinstance(origin, type):
            return GenericAlias(origin, args)
        return args


def _add_identity(cls: type, specs: list[GenericSpec], seen: set[Any]) -> None:
    if cls in seen:
        return
    if not (params := tuple(getattr(cls, "__type_params__", ()))):
        return
    specs.append(
        GenericSpec(
            origin=cls,
            parameters=params,
            arguments=params,
            aligned=True,
            explicit=False,
        )
    )
    seen.add(cls)
