"""
Loader UTIL

-
"""
# NEXT: select best parts
# - check brick.reflect._typearg, way more code...
# TASK: resolve completely, just a few lines in Loader
# -> move rest out of port

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from inspect import Parameter, Signature, signature
from typing import (
    Any,
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

from ..empty import VOID

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
        return f"{_show_params(self.parameters)} -> {shown}"

    def extras(self) -> str:
        parts: list[str] = []
        if self.func_return is not VOID:
            parts.append(f"func={_show(self.func_return)}")
        if self.default_type is not VOID:
            parts.append(f"default={_show(self.default_type)}")
        return ", ".join(parts) or "-"

    def sig(self) -> tuple[str, str]:
        return _show_params(self.parameters), _show(self.value)

    def summary(self) -> str:
        return f"{self.render()} via {self.parameters_source}"


def _show_params(arg: Any) -> str:
    if arg is VOID or arg is Ellipsis:
        return "(...)"
    return _show(arg)


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
    parameters_source: str = source

    def render(self) -> str:
        val: str = "UnTyped" if self.value is VOID else _fmt(self.value)
        return f"{_fmt(self.parameters, is_param=True)} -> {val}"

    def sig(self) -> tuple[str, str]:
        return _fmt(self.parameters, is_param=True), _fmt(self.value)

    def summary(self) -> str:
        return f"{self.render()} via {self.source}"

    @classmethod
    def from_loader(cls, loader) -> Self:
        # def from_loader(cls, loader: Loader[Any, Any]) -> Self:
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


def _extract_generic_pair(loader) -> tuple[Any, Any]:
    # def _extract_generic_pair(loader: Loader[Any, Any]) -> tuple[Any, Any]:
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
        if origin is type(loader):
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
