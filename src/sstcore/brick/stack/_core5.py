"""Fluent attribute stacking: obj.red.bold(x) / obj.key11.key21(x).

Each mapping key becomes a getattr hop that returns a new frozen instance.
__call__ / apply terminates. Bind or attach to reuse the same hops on
existing callables (printer methods, print, pipelines).
"""

import inspect
import keyword
import re
import sys
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field, fields, is_dataclass, replace
from typing import (
    Any,
    ClassVar,
    Literal,
    Self,
    dataclass_transform,
    overload,
)

type Mode = Literal["replace", "append"]
type MappingSource[T] = Mapping[str, T] | Callable[[Any], Mapping[str, T]]
type CallPolicy[S, **P, R] = Callable[
    [S, Callable[P, R], tuple[Any, ...], dict[str, Any]], R
]


@dataclass(frozen=True, slots=True)
class StackLayer[T]:
    """One dimension of stack state (not a public field default — use layer())."""

    mapping: MappingSource[T] | None = None
    mode: Mode = "replace"
    lookup: Callable[[Any, str], T | None] | None = None
    unique: bool = False
    name: str = ""

    def bind_name(self, name: str) -> StackLayer[T]:
        return self if self.name == name else replace(self, name=name)


def layer[T](
    mapping: MappingSource[T] | None = None,
    *,
    lookup: Callable[[Any, str], T | None] | None = None,
    unique: bool = False,
) -> T | None:
    """Replace-mode field default. Annotation is the stored value type."""
    return StackLayer(mapping, mode="replace", lookup=lookup, unique=unique)  # type: ignore[return-value]


def accumulate[T](
    mapping: MappingSource[T] | None = None,
    *,
    lookup: Callable[[Any, str], T | None] | None = None,
    unique: bool = False,
) -> tuple[T, ...]:
    """Append-mode field default. Stored as a tuple."""
    return StackLayer(mapping, mode="append", lookup=lookup, unique=unique)  # type: ignore[return-value]


def _is_layer(value: object) -> bool:
    return isinstance(value, StackLayer)


def _mapping_items[T](
    source: MappingSource[T] | None, obj: object
) -> Mapping[str, T]:
    if source is None:
        return {}
    if callable(source):
        return source(obj)
    return source


def _build_index(
    layers: Sequence[StackLayer[Any]],
) -> dict[str, tuple[StackLayer[Any], Any]]:
    index: dict[str, tuple[StackLayer[Any], Any]] = {}
    for layer_ in layers:
        source = layer_.mapping
        if source is None or callable(source):
            continue
        for key, val in source.items():
            if not key.isidentifier() or keyword.iskeyword(key):
                raise TypeError(
                    f"stack key {key!r} on layer {layer_.name!r} is not a valid identifier"
                )
            if key in index:
                other = index[key][0].name
                raise TypeError(
                    f"duplicate stack key {key!r} on layers {other!r} and {layer_.name!r}"
                )
            index[key] = (layer_, val)
    return index


def _install_layers(cls: type) -> None:
    if cls.__dict__.get("_stack_layers_ready"):
        return

    inherited: tuple[StackLayer[Any], ...] = ()
    for base in cls.__mro__[1:]:
        # EXTRACT:
        found = base.__dict__.get("_stack_layers")
        if found is not None:
            inherited = found
            break

    by_name = {ly.name: ly for ly in inherited if ly.name}
    for name, value in list(cls.__dict__.items()):
        if not _is_layer(value):
            continue
        bound = value.bind_name(name)
        by_name[name] = bound
        setattr(cls, name, () if bound.mode == "append" else None)

    layers = tuple(by_name.values())
    index = _build_index(layers)

    reserved = {
        # EXTRACT:
        "apply",
        "bind",
        "restrict",
        "exclude",
        "configured",
        "stack_keys",
        "generate_stub",
        "from_mappings",
    }
    collisions = reserved & index.keys()
    if collisions:
        raise TypeError(
            f"stack keys collide with StackingCore API: {sorted(collisions)}"
        )
    for ly in layers:
        if ly.name in index:
            raise TypeError(
                f"stack key {ly.name!r} collides with layer field name {ly.name!r}"
            )

    cls._stack_layers = layers
    cls._stack_index = index
    cls._stack_layers_ready = True


def _rebase(cls: type, base: type) -> type:
    # EXTRACT:
    ns = {
        k: v
        for k, v in cls.__dict__.items()
        if k not in {"__dict__", "__weakref__"}
    }
    ns["__module__"] = cls.__module__
    ns["__qualname__"] = getattr(cls, "__qualname__", cls.__name__)
    ns["__annotations__"] = dict(getattr(cls, "__annotations__", {}))
    return type(cls.__name__, (base,), ns)


@overload
def stacking[C: type](cls: C) -> C: ...


@overload
def stacking(
    *,
    frozen: bool = True,
    slots: bool = True,
) -> Callable[[type], type]: ...


@dataclass_transform(frozen_default=True, slots_default=True)
def stacking(
    cls: type | None = None,
    *,
    frozen: bool = True,
    slots: bool = True,
) -> Any:
    """Rebase onto StackingCore and apply a frozen dataclass."""

    def wrap(target: type) -> type:
        if not issubclass(target, StackingCore):
            target = _rebase(target, StackingCore)
        elif not target.__dict__.get("_stack_layers_ready"):
            _install_layers(target)
        if not is_dataclass(target):
            target = dataclass(frozen=frozen, slots=slots)(target)
        return target

    return wrap if cls is None else wrap(cls)


@dataclass(frozen=True)
class StackingCore:
    """Immutable fluent accumulator. Subclass, declare layer fields, implement apply."""

    _stack_path: tuple[str, ...] = field(
        default=(), repr=False, compare=False, kw_only=True
    )
    _allowed: frozenset[str] | None = field(
        default=None, repr=False, compare=False, kw_only=True
    )

    _stack_layers: ClassVar[tuple[StackLayer[Any], ...]] = ()
    _stack_index: ClassVar[dict[str, tuple[StackLayer[Any], Any]]] = {}
    _stack_layers_ready: ClassVar[bool] = True

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        _install_layers(cls)

    def apply(self, value: Any) -> Any:
        """Pure transformation used by bind/attach. Identity by default."""
        return value

    def __call__(self, value: Any) -> Any:
        return self.apply(value)

    def __getattr__(self, name: str) -> Self:
        resolved = self._resolve(name)
        if resolved is None:
            raise AttributeError(
                f"{type(self).__name__!r} has no stack key {name!r}"
            )
        layer_, value = resolved
        return self._evolve(layer_, value, name)

    def __getitem__(self, name: str) -> Self:
        return self.__getattr__(name)

    def __dir__(self) -> list[str]:
        names = set(super().__dir__())
        names.update(self._visible_keys())
        return sorted(names)

    def __repr__(self) -> str:
        cls = type(self).__name__
        if self._stack_path:
            return f"{cls}.{'.'.join(self._stack_path)}"
        return f"{cls}()"

    @property
    def configured(self) -> bool:
        for layer_ in type(self)._stack_layers:
            current = getattr(self, layer_.name)
            if layer_.mode == "append":
                if current:
                    return True
            elif current is not None:
                return True
        return False

    @classmethod
    def stack_keys(cls) -> tuple[str, ...]:
        return tuple(cls._stack_index)

    def restrict(self, *keys: str) -> Self:
        extra = frozenset(keys)
        current = self._allowed
        allowed = extra if current is None else current & extra
        return replace(self, _allowed=allowed)

    def exclude(self, *keys: str) -> Self:
        blocked = frozenset(keys)
        visible = self._visible_keys() - blocked
        return replace(self, _allowed=frozenset(visible))

    def bind[**P, R](
        self,
        fn: Callable[P, R],
        *,
        policy: CallPolicy[Self, P, R] | None = None,
    ) -> BoundStack[Self, P, R]:
        return BoundStack(self, fn, policy or first_str_arg)

    def _visible_keys(self) -> set[str]:
        names = set(type(self)._stack_index)
        for layer_ in type(self)._stack_layers:
            if callable(layer_.mapping):
                names.update(_mapping_items(layer_.mapping, self))
        if self._allowed is not None:
            names &= self._allowed
        return names

    def _resolve(self, name: str) -> tuple[StackLayer[Any], Any] | None:
        if self._allowed is not None and name not in self._allowed:
            return None
        index = type(self)._stack_index
        if name in index:
            return index[name]
        for layer_ in type(self)._stack_layers:
            if layer_.lookup is not None:
                found = layer_.lookup(self, name)
                if found is not None:
                    return layer_, found
            source = layer_.mapping
            if callable(source):
                mapping = source(self)
                if name in mapping:
                    return layer_, mapping[name]
        return None

    def _evolve(self, layer_: StackLayer[Any], value: Any, key: str) -> Self:
        current = getattr(self, layer_.name)
        if layer_.mode == "append":
            if layer_.unique and value in current:
                new = current
            else:
                new = (*current, value)
        else:
            new = value
        return replace(
            self,
            **{
                layer_.name: new,
                "_stack_path": (*self._stack_path, key),
            },
        )

    @classmethod
    def from_mappings(
        cls,
        mappings: Sequence[Mapping[str, Any]],
        apply: Callable[..., Any],
        *,
        names: Sequence[str] | None = None,
        modes: Sequence[Mode] | None = None,
    ) -> type[StackingCore]:
        """Untyped factory: list of mappings + injected sink."""
        n = len(mappings)
        field_names = (
            tuple(names)
            if names is not None
            else tuple(f"attr{i + 1}" for i in range(n))
        )
        if len(field_names) != n:
            raise ValueError("names must match mappings")
        used_modes: Sequence[Mode] = (
            modes if modes is not None else ("replace",) * n
        )
        if len(used_modes) != n:
            raise ValueError("modes must match mappings")

        ns: dict[str, Any] = {"__annotations__": {}}
        for fname, mapping, mode in zip(
            field_names, mappings, used_modes, strict=True
        ):
            ns[fname] = (
                accumulate(mapping) if mode == "append" else layer(mapping)
            )
            ns["__annotations__"][fname] = Any

        def _apply(self: StackingCore, *args: Any, **kwargs: Any) -> Any:
            return apply(self, *args, **kwargs)

        ns["apply"] = _apply
        built = type(f"{cls.__name__}FromMaps", (cls,), ns)
        return dataclass(frozen=True, slots=True)(built)

    @classmethod
    def generate_stub(cls) -> str:
        """Stub pyi body: explicit properties so the IDE can autocomplete keys."""

        # EXTRACT:
        cls_name = cls.__name__
        lines = [f"class {cls_name}:"]
        if is_dataclass(cls):
            for f in fields(cls):
                if f.name.startswith("_"):
                    continue
                anno = getattr(f.type, "__name__", repr(f.type))
                lines.append(f"    {f.name}: {anno}")
        if callable(cls):
            try:
                sig = inspect.signature(cls.__call__)
                lines.append(f"    def __call__{sig}: ...")
            except TypeError, ValueError:
                lines.append("    def __call__(self, *args, **kwargs): ...")
        for key in sorted(cls._stack_index):
            lines.append("    @property")
            lines.append(f"    def {key}(self) -> {cls_name}: ...")
        if len(lines) == 1:
            lines.append("    ...")
        return "\n".join(lines) + "\n"


@dataclass(frozen=True, slots=True)
class BoundStack[S: StackingCore, **P, R]:
    """Stack hops first, then call `fn` through `policy`."""

    stack: S
    fn: Callable[P, R]
    policy: CallPolicy[S, P, R] = field(repr=False)

    def __getattr__(self, name: str) -> Any:
        value = getattr(self.stack, name)
        if isinstance(value, type(self.stack)):
            return BoundStack(value, self.fn, self.policy)
        return value

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.policy(self.stack, self.fn, args, kwargs)

    def __dir__(self) -> list[str]:
        return dir(self.stack)

    def __repr__(self) -> str:
        return f"{self.stack!r}.bind({self.fn!r})"

    def restrict(self, *keys: str) -> BoundStack[S, P, R]:
        return replace(self, stack=self.stack.restrict(*keys))


def first_str_arg[S: StackingCore, **P, R](
    stack: S,
    fn: Callable[P, R],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> R:
    """Style the first str argument, then call fn (print/header-shaped APIs)."""
    if args and isinstance(args[0], str):
        args = (stack.apply(args[0]), *args[1:])
    return fn(*args, **kwargs)  # type: ignore[arg-type]


def style_str_args[S: StackingCore, **P, R](
    stack: S,
    fn: Callable[P, R],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> R:
    apply = stack.apply
    args = tuple(apply(a) if isinstance(a, str) else a for a in args)
    kwargs = {
        k: apply(v) if isinstance(v, str) else v for k, v in kwargs.items()
    }
    return fn(*args, **kwargs)  # type: ignore[arg-type]


def style_result[S: StackingCore, **P, R](
    stack: S,
    fn: Callable[P, R],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> R:
    return stack.apply(fn(*args, **kwargs))  # type: ignore[arg-type]


class Stacked[S: StackingCore, **P, R]:
    """Method descriptor: printer.header.bold.green("x")."""

    def __init__(
        self,
        stack_cls: type[S],
        *,
        allow: Sequence[str] | None = None,
        policy: CallPolicy[S, Any, Any] | None = None,
    ) -> None:
        self.stack_cls = stack_cls
        self.allow = tuple(allow) if allow is not None else None
        self.policy = policy or first_str_arg
        self.fn: Callable[Any, Any] | None = None

    def __call__(self, fn: Callable[P, R]) -> Stacked[S, P, R]:
        self.fn = fn
        return self

    def __set_name__(self, owner: type, name: str) -> None:
        if self.fn is None:
            self.fn = getattr(owner, name, None)

    def __get__(
        self, obj: object | None, owner: type | None = None
    ) -> BoundStack[S, P, R] | Stacked[S, P, R]:
        if obj is None:
            return self
        fn = self.fn
        if fn is None:
            raise TypeError("Stacked descriptor is not bound to a function")
        stack: S = self.stack_cls()
        if self.allow is not None:
            stack = stack.restrict(*self.allow)

        def invoke(*args: P.args, **kwargs: P.kwargs) -> R:
            return fn(obj, *args, **kwargs)

        return BoundStack(stack, invoke, self.policy)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class StackProxy[S: StackingCore]:
    """Both orders: proxy.header.red("x") and proxy.red.header("x")."""

    target: Any
    stack: S
    policy: CallPolicy[S, Any, Any] = field(default=first_str_arg, repr=False)

    def __getattr__(self, name: str) -> Any:
        stack = object.__getattribute__(self, "stack")
        target = object.__getattribute__(self, "target")
        policy = object.__getattribute__(self, "policy")

        stack_next: Any = None
        try:
            stack_next = getattr(stack, name)
        except AttributeError:
            pass

        target_attr = getattr(target, name, None)
        target_hit = not (target_attr is None and not hasattr(target, name))

        if (
            stack_next is not None
            and isinstance(stack_next, type(stack))
            and target_hit
            and callable(target_attr)
        ):
            raise AttributeError(
                f"{name!r} exists on both stack and target; rename one of them"
            )
        if stack_next is not None and isinstance(stack_next, type(stack)):
            return StackProxy(target, stack_next, policy)
        if target_hit:
            if callable(target_attr):
                return BoundStack(stack, target_attr, policy)
            return target_attr
        raise AttributeError(name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        target = object.__getattribute__(self, "target")
        stack = object.__getattribute__(self, "stack")
        policy = object.__getattribute__(self, "policy")
        if not callable(target):
            raise TypeError(f"{type(target).__name__} is not callable")
        return policy(stack, target, args, kwargs)


def attach[S: StackingCore](
    target: Any,
    stack: S,
    *,
    policy: CallPolicy[S, Any, Any] | None = None,
) -> StackProxy[S]:
    return StackProxy(target, stack, policy or first_str_arg)


#  LINE: -- Usage -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@stacking
class Greeter:
    times: int | None = layer({"key11": 2, "key12": 3, "key13": 5})
    greeting: str | None = layer({"key21": "hello", "key22": "bye"})
    transform: Callable[[str], str] | None = layer(
        {"key31": str.lower, "key32": str.capitalize, "key33": str.upper}
    )

    def apply(self, target: str) -> str:
        text = f"{target} says {self.greeting} to Peter"
        if self.transform is not None:
            text = self.transform(text)
        for _ in range(self.times or 1):
            print(text)
        return text


handler_stack = Greeter()
handler_stack.key11.key21.key31("Alice")

type AttrType[Value] = dict[str, Value]
ATTR1: AttrType[int] = {
    "key11": 2,
    "key12": 3,
    "key13": 5,
}
ATTR2: AttrType[str] = {
    "key21": "hello",
    "key22": "bye",
}
ATTR3: AttrType[Callable[[str], str]] = {
    "key31": str.lower,
    "key32": str.capitalize,
    "key33": str.upper,
}

GreeterDyn = StackingCore.from_mappings(
    [ATTR1, ATTR2, ATTR3],
    apply=lambda self, target: ...,
    names=("times", "greeting", "transform"),
    modes=("replace", "replace", "replace"),
)

#  LINE: -- ColorStack -- -- - -- -- - -- -- - -- -- - -- -- - -- --


ANSI_COLORS = {"red": "\033[31m", "green": "\033[32m", "blue": "\033[34m"}
ANSI_MODIFIERS = {"bold": "\033[1m", "underline": "\033[4m"}
RESET = "\033[0m"


def _color_from_box(self: Any, name: str) -> str | None:
    box = getattr(self, "box_ref", None)
    if box is None:
        return None
    getter = getattr(box, "get", None)
    if getter is None:
        return None
    try:
        return getter(name)
    except KeyError, AttributeError:
        return None


@stacking
class ColorStack:
    box_ref: Any | None = None
    color: str | None = layer(ANSI_COLORS, lookup=_color_from_box)
    modifiers: tuple[str, ...] = accumulate(ANSI_MODIFIERS, unique=True)

    def apply(self, text: str) -> str:
        if not self.configured:
            return text
        prefix = "".join(self.modifiers)
        if self.color:
            prefix += self.color
        return f"{prefix}{text}{RESET}" if prefix else text


class ColorBox:
    def __init__(self) -> None:
        self._stack = ColorStack(box_ref=self)

    def __getattr__(self, name: str) -> ColorStack:
        return getattr(self._stack, name)


colorbox = ColorBox()
colorbox.red.bold("title")

#  LINE: -- Printer -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Printer:
    @Stacked(ColorStack, allow=("bold", "underline", "green", "blue"))
    def header(self, text: str) -> None:
        print(text)

    @Stacked(ColorStack, allow=("red", "bold"))
    def error(self, text: str) -> None:
        print(text, file=sys.stderr)


printer = Printer()

printer.header.bold.green("My Header")
printer.error.red("boom")
printer.header.red(...)  # -> AttributeError

cprint = attach(print, ColorStack())
cprint.red.bold("hello")
cprint.bold.green("hello")

styled = attach(printer, ColorStack())
styled.header.bold.green("x")
styled.bold.green.header("x")


#  LINE: -- Format -- -- - -- -- - -- -- - -- -- - -- -- - -- --


type StrFn = Callable[[str], str]

NORMALIZERS: dict[str, StrFn] = {
    "nfc": lambda s: unicodedata.normalize("NFC", s),
    "lower": str.lower,
    "upper": str.upper,
    "casefold": str.casefold,
}
SANITIZERS: dict[str, StrFn] = {
    "strip": str.strip,
    "collapse": lambda s: re.sub(r"\s+", " ", s),
    "alnum": lambda s: re.sub(r"[^0-9A-Za-z ]+", "", s),
}
FORMATTERS: dict[str, StrFn] = {
    "title": str.title,
    "repr": repr,
}


@stacking
class StringPipeline:
    # EXTRACT:
    normalize: tuple[StrFn, ...] = accumulate(NORMALIZERS)
    sanitize: tuple[StrFn, ...] = accumulate(SANITIZERS)
    format_: tuple[StrFn, ...] = accumulate(FORMATTERS)
    color: ColorStack | None = None  # set via a hop or bind

    def apply(self, text: str) -> str:
        for fn in (*self.normalize, *self.sanitize, *self.format_):
            text = fn(text)
        if self.color is not None:
            text = self.color.apply(text)
        return text


clean = StringPipeline().nfc.strip.collapse
colored = attach(clean, ColorStack(), policy=style_result)
colored.red.bold("  Café   ")  # normalize/sanitize first, then color

print(ColorStack.generate_stub())
# class ColorStack:
#     color: str
#     modifiers: tuple
#     def __call__(self, value): ...
#     @property
#     def red(self) -> ColorStack: ...
