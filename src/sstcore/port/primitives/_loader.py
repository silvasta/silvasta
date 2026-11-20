"""
Loader

-
"""

__all__: list[str] = [
    "LoaderClsInput",
    "LoaderInput",
    "Prefer",
    "LoadFunc",
    "Loading",
    "Loader",
]


import typing as _t
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from inspect import Parameter, Signature, signature
from typing import (
    Any,
    Generic,
    Literal,
    NamedTuple,
    ParamSpec,
    Protocol,
    Self,
    TypedDict,
    TypeVar,
    TypeVarTuple,
    get_args,
    get_origin,
)
from typing import Unpack as _U  # noqa: N814

from ..empty import VOID, MayBe, MayNot


class LoadFunc[**P, Target](_t.Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Target:
        """Define the Typed and Parametrized Call of the Loader"""


type Loading[**P, T] = Loader[P, T] | LoadFunc[P, T]
type Prefer = Literal["func", "default"]


class LoaderInput[T](_t.TypedDict, total=False):
    """Define the Base for the Typed Kwargs"""

    default: MayBe[T]
    prefer: Prefer


class _LoaderClsInput[P, T](_t.TypedDict, total=False):
    loader: Loader[[P], T] | Loading[[P], T] | None


class LoaderClsInput(_LoaderClsInput, LoaderInput, TypedDict):
    """Extend the Base with the Loader Cls itself"""


class Loader[**P, T]:
    """Govern the tools and state for predefined Loading"""

    Input = LoaderInput  # TEST:
    Func = LoadFunc  # TEST:

    @property
    def value(self) -> T:
        """Provide the loaded Value or Raise"""
        if self._value is not VOID:
            return self._value
        raise LookupError(f"{self!r} has neither a callable nor a default")

    @property
    def is_ready(self) -> bool:
        return self._value is not VOID

    def __init__(self, func: MayNot[Func[P, T]] = None, /, **tkw: _U[Input[T]]):
        """So far no check if Loader can complete, use Loader.__bool__"""
        self._func: MayNot[Loader.Func[P, T]] = func
        self._default: MayBe[T] = tkw.get("default", VOID)
        self._prefer: Prefer = tkw.get("prefer", "func")

        self._counter: int = 0
        self._total_counter: int = 0
        self._value: MayBe[T] = VOID

    def bind(self, fn: Callable[P, T]) -> Callable[P, T]:
        """Attach or replace the loader callable and reset execution state"""
        self._func: Loader.Func[P, T] = fn
        self.reset()
        return fn

    def clone(self) -> Self:
        """Copy same Configuration but with fresh State and Value"""
        return type(self)(
            self._func, default=self._default, prefer=self._prefer
        )

    @classmethod
    def loading(
        cls, loading: MayNot[Loading[P, T]], /, **tkw: _U[Input[T]]
    ) -> Self:
        """Create from existing loader, function or just from kwargs"""
        return (
            loading.clone().updated(**tkw)  # ty:ignore
            if isinstance(loading, Loader)
            else cls(loading, **tkw)
        )

    def updated(self, **tkw: _t.Unpack[Input[T]]) -> Self:
        if (default := tkw.get("default", VOID)) is not VOID:
            self._default: T | VOID = default
        if (prefer := tkw.get("prefer", VOID)) is not VOID:
            self._prefer: Prefer = prefer
        return self

    def reset(self) -> int:
        """Delete the fetched Value and reset and provide the current Counter"""
        _counted, self._counter = self._counter, 0
        self._value: VOID = VOID
        return _counted

    def install(self, *args: P.args, **kwargs: P.kwargs) -> MayBe[T]:
        """Fetch Value or Assign from launched Loaders in Prefered Order"""
        if self.is_ready:
            return self._value
        for loader in self._order():
            if (value := loader(*args, **kwargs)) is not VOID:
                self._value: T | VOID = value
                return value
        return VOID

    def _order(self) -> Iterator:
        """Provide Locations in Prefered Order to Install new Value"""
        loaders: list[LoadFunc] = [
            lambda *a, **k: self._counted_call(*a, **k),
            lambda *_, **__: self._default,
        ]
        # NEXT:
        # NEXT:
        # NEXT:
        # NEXT:
        match self._prefer:
            case "func":
                yield from loaders
            case "default":
                yield from reversed(loaders)

    def _counted_call(self, *args: P.args, **kwargs: P.kwargs) -> MayBe[T]:
        """Increment Counter on Launch of Loader Function"""
        self._counter += 1
        self._total_counter += 1
        return self.call(*args, **kwargs)

    def call(self, *args: P.args, **kwargs: P.kwargs) -> MayBe[T]:
        """Execute Loader Function if assigned without any State change"""
        if self._func is None:
            return VOID
        return self._func(*args, **kwargs)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        """Extract or Install Value by configured order or Raise if Empty"""
        self.install(*args, **kwargs)
        return self.value

    def __bool__(self) -> bool:
        """True if either a callable or a static default is configured."""
        return self._func is not None or self._default is not VOID

    def __str__(self) -> str:
        _maybe_value = f"{self.value}::" if self._value is not VOID else ""
        _type_args = self.type_args.render()
        return f"{type(self).__name__}[{_maybe_value}{_type_args}]"

    def __repr__(self) -> str:
        func: str = getattr(self._func, "__name__", repr(self._func))
        default: str = repr(self._default)
        prefer: str = self._prefer
        counter = f"{self._counter}/{self._total_counter}"
        types: str = self.type_args.summary()
        return f"{self}({func=}, {default=}, {prefer=}, {counter=}, {types=})"

    #  LINE: -- Experimental -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __class_getitem__(cls, params: Any) -> Any:
        return _LoaderAlias(cls, params)

    @property
    def type_args(self) -> TypeArg:
        return TypeArg.from_loader(self)

    @property
    def _type_args(self) -> TypeView:
        return type_view(self, Loader)

    @property
    def target_type(self) -> Any:
        return self.type_args.value


#  LINE: -- TypeArg Helper -- -- - -- -- - -- -- - -- -- - -- -- - -- --


_PARAM = (TypeVar, ParamSpec, TypeVarTuple)
_SKIP = (Generic, Protocol)


class TypeView(NamedTuple):
    value: Any
    parameters: Any
    value_source: str
    parameters_source: str
    func_return: Any
    default_type: Any

    def render(self) -> str:
        shown = "UnTyped" if self.value is VOID else _show(self.value)
        return f"{_show_params(self.parameters)}, {shown}"

    def extras(self) -> str:
        parts: list[str] = []
        if self.func_return is not VOID:
            parts.append(f"func={_show(self.func_return)}")
        if self.default_type is not VOID:
            parts.append(f"default={_show(self.default_type)}")
        return ", ".join(parts) or "-"


def type_view(loader: Any, origin: type) -> TypeView:
    declared = _pair(loader, origin)
    func_params, func_return = (
        _signature_types(loader._func)
        if loader._func is not None
        else (VOID, VOID)
    )
    default_type: Any = (
        VOID
        if loader._default is VOID
        else None
        if loader._default is None
        else type(loader._default)
    )
    d_params, d_value = declared if declared is not None else (VOID, VOID)
    if _concrete(d_value):
        value, value_source = d_value, "generic"
    elif _concrete(func_return):
        value, value_source = func_return, "func"
    elif default_type is not VOID:
        value, value_source = default_type, "default"
    elif isinstance(d_value, _PARAM):
        value, value_source = d_value, "unbound"
    else:
        value, value_source = VOID, "none"
    if d_params is not VOID:
        parameters, parameters_source = d_params, "generic"
    elif func_params is not VOID:
        parameters, parameters_source = func_params, "func"
    else:
        parameters, parameters_source = Ellipsis, "unknown"
    return TypeView(
        value,
        parameters,
        value_source,
        parameters_source,
        func_return,
        default_type,
    )


def _pair(obj: Any, origin: type) -> tuple[Any, Any] | None:
    env: dict[Any, Any] = {}
    found: tuple[Any, ...] | None = None

    def take(alias: Any) -> None:
        nonlocal found
        owner = get_origin(alias)
        if not isinstance(owner, type) or owner in _SKIP:
            return
        params = tuple(getattr(owner, "__type_params__", ()))
        aligned = _align(params, tuple(_subst(a, env) for a in get_args(alias)))
        if len(params) != len(aligned):
            return
        if owner is origin and found is None:
            found = aligned
        for param, arg in zip(params, aligned, strict=False):
            if isinstance(param, _PARAM) and param not in env:
                env[param] = arg

    if not isinstance(obj, type) and (
        stamped := getattr(obj, "__orig_class__", None)
    ):
        take(stamped)
    cls = obj if isinstance(obj, type) else type(obj)
    for klass in cls.__mro__:
        for base in getattr(klass, "__orig_bases__", ()):
            take(base)
    if found is None:
        return None
    if len(found) == 2:
        return found[0], found[1]
    named = {
        getattr(param, "__name__", ""): arg
        for param, arg in zip(
            getattr(origin, "__type_params__", ()), found, strict=False
        )
    }
    return named.get("P", VOID), named.get("T", found[-1])


def _align(params: tuple[Any, ...], args: tuple[Any, ...]) -> tuple[Any, ...]:
    idxs = [
        i
        for i, param in enumerate(params)
        if isinstance(param, (ParamSpec, TypeVarTuple))
    ]
    if len(idxs) != 1:
        return args
    index, tail = idxs[0], len(params) - idxs[0] - 1
    if len(args) < index + tail:
        return args
    mid = args[index : len(args) - tail if tail else len(args)]
    token = mid[0] if len(mid) == 1 else None
    if isinstance(params[index], ParamSpec) and (
        token is Ellipsis
        or getattr(get_origin(token), "__name__", None) == "Concatenate"
    ):
        packed: Any = token
    elif len(mid) == 1 and isinstance(mid[0], tuple):
        packed = mid[0]
    else:
        packed = mid
    return args[:index] + (packed,) + (args[-tail:] if tail else ())


def _subst(arg: Any, env: Mapping[Any, Any]) -> Any:
    if not env:
        return arg
    if isinstance(arg, _PARAM):
        return env.get(arg, arg)
    if isinstance(arg, tuple):
        return tuple(_subst(item, env) for item in arg)
    owner, raw = get_origin(arg), get_args(arg)
    if owner is None or not raw:
        return arg
    updated = tuple(_subst(item, env) for item in raw)
    if updated == raw:
        return arg
    try:
        return owner[updated[0]] if len(updated) == 1 else owner[updated]
    except TypeError:
        return arg


def _signature_types(func: Callable[..., Any]) -> tuple[Any, Any]:
    try:
        sig = signature(func)
    except TypeError, ValueError:
        return VOID, VOID
    try:
        hints = __import__("typing").get_type_hints(func)
    except NameError, TypeError, ValueError:
        hints = {}
    returned = hints.get("return", sig.return_annotation)
    if returned is Signature.empty:
        returned = VOID
    params = tuple(
        hints.get(
            name,
            Any if param.annotation is Signature.empty else param.annotation,
        )
        for name, param in sig.parameters.items()
    )
    return params, returned


def _show(arg: Any) -> str:
    if arg is VOID:
        return "VOID"
    if arg is Ellipsis:
        return "..."
    if arg is None:
        return "None"
    if isinstance(arg, type):
        return arg.__qualname__
    if isinstance(arg, tuple):
        return "(" + ", ".join(_show(item) for item in arg) + ")"
    if isinstance(arg, _PARAM) or isinstance(
        getattr(arg, "__name__", None), str
    ):
        return arg.__name__
    return str(arg).removeprefix("typing.")


def _show_params(arg: Any) -> str:
    if arg is VOID or arg is Ellipsis:
        return "(...)"
    return _show(arg)


def _concrete(arg: Any) -> bool:
    if arg is VOID or arg is Ellipsis or isinstance(arg, _PARAM):
        return False
    if isinstance(arg, tuple):
        return all(_concrete(item) for item in arg)
    return True


#  LINE: -- TypeArg Helper -- -- - -- -- - -- -- - -- -- - -- -- - -- --
#  LINE: -- TypeArg Helper -- -- - -- -- - -- -- - -- -- - -- -- - -- --
#  LINE: -- TypeArg Helper -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _LoaderAlias:
    """Lightweight generic alias preserving __orig_class__ on instantiation."""

    __slots__ = ("__origin__", "__args__")

    def __init__(self, origin: type, /, params: Any) -> None:
        self.__origin__: type = origin
        self.__args__: tuple[Any, ...] = (
            params if isinstance(params, tuple) else (params,)
        )

    def __mro_entries__(self, bases: tuple[Any, ...]) -> tuple[type, ...]:
        _ = bases
        return (self.__origin__,)

    def __call__(self, *args, **kwargs) -> Any:
        unit: Any = self.__origin__(*args, **kwargs)
        unit.__orig_class__ = self
        return unit


@dataclass(frozen=True, slots=True)
class TypeArg:
    """Minimal best-effort type visualizer for port.Loader."""

    parameters: Any = Ellipsis
    value: Any = VOID
    source: str = "none"

    def render(self) -> str:
        val: str = "UnTyped" if self.value is VOID else _fmt(self.value)
        return f"{_fmt(self.parameters, is_param=True)}, {val}"

    def summary(self) -> str:
        return f"{self.render()} via {self.source}"

    @classmethod
    def from_loader(cls, loader: Loader[Any, Any]) -> Self:
        g_params, g_val = _extract_generic_pair(loader)
        f_params, f_val = _extract_func_pair(loader._func)

        # 1. Resolve Value (T): concrete generic > func annotation > default > unbound TypeVar
        if _is_concrete(g_val):
            val, src = g_val, "generic"
        elif _is_concrete(f_val):
            val, src = f_val, "func"
        elif loader._default is not VOID:
            val = None if loader._default is None else type(loader._default)
            src = "default"
        elif g_val is not VOID:
            val, src = g_val, "unbound"
        else:
            val, src = VOID, "none"

        # 2. Resolve Parameters (P): generic > func annotation > Ellipsis
        params = (
            g_params
            if g_params is not VOID
            else (f_params if f_params is not VOID else Ellipsis)
        )
        return cls(parameters=params, value=val, source=src)


def _extract_generic_pair(loader: Loader[Any, Any]) -> tuple[Any, Any]:
    aliases = [getattr(loader, "__orig_class__", None)]
    for klass in type(loader).__mro__:
        aliases.extend(getattr(klass, "__orig_bases__", ()))

    env: dict[Any, Any] = {}
    for alias in aliases:
        origin = getattr(alias, "__origin__", None)
        args = getattr(alias, "__args__", ())
        if not origin or not args:
            continue
        args = tuple(env.get(a, a) for a in args)
        tparams = getattr(origin, "__type_params__", ())
        if len(tparams) == len(args):
            env.update(zip(tparams, args, strict=False))
        if origin is Loader:
            return (
                (args[0], args[1]) if len(args) == 2 else (args[:-1], args[-1])
            )
    return VOID, VOID


def _extract_func_pair(func: Any) -> tuple[Any, Any]:
    if func is None:
        return VOID, VOID
    try:
        sig = signature(func)
    except TypeError, ValueError:
        return VOID, VOID
    params = tuple(
        Any if p.annotation is Parameter.empty else p.annotation
        for p in sig.parameters.values()
    )
    ret = (
        VOID
        if sig.return_annotation is Signature.empty
        else sig.return_annotation
    )
    return params, ret


def _is_concrete(tp: Any) -> bool:
    return (
        tp is not VOID
        and tp is not Ellipsis
        and not isinstance(tp, (TypeVar, ParamSpec))
    )


def _fmt(tp: Any, *, is_param: bool = False) -> str:
    if tp is VOID or tp is Ellipsis:
        return "(...)" if is_param else "..."
    if tp is None:
        return "None"
    if isinstance(tp, (tuple, list)):
        return "(" + ", ".join(_fmt(x) for x in tp) + ")"
    if isinstance(tp, type):
        return tp.__qualname__
    return getattr(tp, "__name__", str(tp)).removeprefix("typing.")
