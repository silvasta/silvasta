"""
Loader

-
"""

__all__: list[str] = [
    "Loader",
    "LoaderInput",
    "Loading",
    "Prefer",
]


import typing as _t
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from inspect import Signature, signature
from typing import Any, Literal, Self

from ..empty import VOID, MayBe, MayNot
from . import _typearg
from ._typearg import format_type_arg


class Loading[**P, Target](_t.Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Target:
        """Define the Requirements for Loading the Loader Value"""


class LoaderInput[T](_t.TypedDict, total=False):
    default: MayBe[T]
    prefer: Prefer


type Prefer = Literal["func", "default"]


class Loader[**P, T]:
    """Stateful lazy callable + static default resolver with selectable order."""  # NEXT:

    def __init__(
        self,
        func: MayNot[Loading[P, T]] = None,
        /,
        **tkw: _t.Unpack[LoaderInput[T]],
    ):
        self._func: MayNot[Loading[P, T]] = func
        self._default: MayBe[T] = tkw.get("default", VOID)
        self._prefer: Prefer = tkw.get("prefer", "func")

        self._counter: int = 0
        self._total_counter: int = 0
        self._value: MayBe[T] = VOID

    def __str__(self) -> str:
        _maybe_value = "" if self._value is VOID else f"{self.value}::"
        _type_args = self.type_args.render()
        return f"{type(self).__name__}[{_maybe_value}{_type_args}]"

    def __repr__(self) -> str:
        func: str = getattr(self._func, "__name__", repr(self._func))
        default: str = repr(self._default)
        prefer: str = self._prefer
        counter = f"{self._counter}/{self._total_counter}"
        types: str = self.type_args.summary()
        return f"{self}({func=}, {default=}, {prefer=}, {counter=}, {types=})"

    def __bool__(self) -> bool:
        """True if either a callable or a static default is configured."""
        return self._func is not None or self._default is not VOID

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        """Extract or Install Value by configured order or Raise if Empty"""
        self.install(*args, **kwargs)
        return self.value

    @property
    def value(self) -> T:
        """Provide Extracted Value or Raise"""
        if self._value is not VOID:
            return self._value
        raise LookupError(f"{self!r} has neither a callable nor a default")

    @property
    def is_ready(self) -> bool:
        """Everything Loaded?"""
        return self._value is not VOID

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
        # NOTE: latest when 3 dispatches occur... it will be difficult
        loaders: list[Loading] = [
            lambda *a, **k: self._counted_call(*a, **k),
            lambda *_, **__: self._default,
        ]
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

    def bind(self, fn: Callable[P, T]) -> Callable[P, T]:
        """Attach or replace the loader callable and reset execution state"""
        self._func: Loading[P, T] = fn
        self.reset()
        return fn

    def clone(self) -> Self:
        """Establish Copy with same configuration but without State and Value"""
        return type(self)(
            self._func, default=self._default, prefer=self._prefer
        )

    def reset(self) -> int:
        """Delete the fetched Value and reset and provide the current Counter"""
        _counted, self._counter = self._counter, 0
        self._value: VOID = VOID
        return _counted

    #  LINE: -- Experimental -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    if not _typearg.preserves_generic_alias_on_instance():

        def __class_getitem__(cls, params: Any) -> Any:
            return _typearg.remembering_getitem(cls, params)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        _typearg.normalize_orig_bases(cls)

    @property
    def type_args(self) -> LoaderTypes:
        """Full spectrum and the resolved ``(P, T)`` pair."""
        return resolve_loader_types(self)

    @property
    def target_type(self) -> Any:
        """Resolved value type. VOID when no channel produced one.

        Open TypeVars are returned as themselves. The parameter list and
        the unused channels are on ``type_args``, not here.
        """
        return self.type_args.value


#  LINE: -- TypeArg Helper -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# AI: why is this copy of _typearg.format_type_arg here?
# def _format_parameters(arg: Any) -> str:
#     if arg is VOID or arg is Ellipsis:
#         return "(...)"
#     if isinstance(arg, tuple):
#         return "(" + ", ".join(format_type_arg(item) for item in arg) + ")"
#     return format_type_arg(arg)


@dataclass(frozen=True, slots=True)
class LoaderTypes:
    """Spectrum plus the one pair ``__str__`` should show.

    ``specs`` is everything the extractor found, including an implicit
    identity spec. ``value`` and ``parameters`` are the resolved pair.
    """

    specs: tuple[_typearg.GenericSpec, ...]
    value: Any
    parameters: Any
    value_source: str
    parameters_source: str
    func_return: Any = VOID
    func_parameters: Any = VOID
    default_type: Any = VOID

    def render(self) -> str:
        value = "UnTyped" if self.value is VOID else format_type_arg(self.value)
        return f"{format_type_arg(self.parameters)}, {value}"

    def summary(self) -> str:
        explicit = ", ".join(str(spec) for spec in self.specs if spec.explicit)
        generic: str = explicit or "-"
        return f"{self.render()} via {self.value_source}; generic=[{generic}]"


def _declared_spec(
    specs: tuple[_typearg.GenericSpec, ...], origin: type
) -> MayNot[_typearg.GenericSpec]:
    for spec in specs:
        if spec.is_to_declare(origin):
            return spec
    return None


def _looks_generic(target: Any) -> bool:
    if (
        not isinstance(target, type)
        and getattr(target, "__orig_class__", None) is not None
    ):
        return True
    cls = target if isinstance(target, type) else type(target)
    for klass in cls.__mro__:
        if getattr(klass, "__type_params__", ()):
            return True
        if getattr(klass, "__orig_bases__", ()):
            return True
    return False


def _pick_value(
    declared: _typearg.GenericSpec | None,
    func_return: Any,
    default_type: Any,
) -> tuple[Any, str]:
    declared_value = VOID if declared is None else declared.get("T")

    if _typearg.is_concrete_type(declared_value):
        return declared_value, "generic"
    if _typearg.is_concrete_type(func_return):
        return func_return, "func"
    if default_type is not VOID:
        return default_type, "default"
    if _typearg.is_type_parameter(declared_value):
        return declared_value, "unbound"

    return VOID, "none"


def _pick_parameters(
    declared: _typearg.GenericSpec | None,
    func_parameters: Any,
) -> tuple[Any, str]:
    if declared is not None:
        declared_parameters = declared.get("P")
        if declared_parameters is not VOID:
            return declared_parameters, "generic"

    if func_parameters is not VOID:
        return func_parameters, "func"

    return Ellipsis, "unknown"


def resolve_loader_types(loader: Loader) -> LoaderTypes:
    """Merge generic specialization with this loader's own channels.

    The extractor runs only when the object looks generic. A similar class
    that is not generic skips it and still uses the callable and default.
    """
    specs = _typearg.extract_type_args(loader) if _looks_generic(loader) else ()
    declared = _declared_spec(specs, Loader)

    func_parameters: Any = VOID
    func_return: Any = VOID
    if loader._func is not None:
        func_parameters, func_return = _signature_types(loader._func)

    if loader._default is VOID:
        default_type: Any = VOID
    elif loader._default is None:
        default_type = None
    else:
        default_type = type(loader._default)

    value, value_source = _pick_value(declared, func_return, default_type)
    parameters, parameters_source = _pick_parameters(declared, func_parameters)
    return LoaderTypes(
        specs=specs,
        value=value,
        parameters=parameters,
        value_source=value_source,
        parameters_source=parameters_source,
        func_return=func_return,
        func_parameters=func_parameters,
        default_type=default_type,
    )


def _signature_types(func: Callable[..., Any]) -> tuple[Any, Any]:
    """``(parameter types, return type)`` from annotations, not inference.

    Failure of either ``signature`` or ``get_type_hints`` degrades that
    side to VOID or to the raw annotation. An empty parameter tuple is a
    real answer (``Loader[(), str]``), so it is not VOID.
    """
    try:
        sig = signature(func)
    except TypeError, ValueError:
        return VOID, VOID

    hints: dict[str, Any] | None
    try:
        hints = _t.get_type_hints(func)
    except NameError, TypeError, ValueError:
        hints = None

    if hints is not None and "return" in hints:
        returned: Any = hints["return"]
    else:
        returned = sig.return_annotation
        if returned is Signature.empty:
            returned = VOID

    parameters: list[Any] = []
    for name, param in sig.parameters.items():
        if hints is not None and name in hints:
            parameters.append(hints[name])
        elif param.annotation is not Signature.empty:
            parameters.append(param.annotation)
        else:
            parameters.append(Any)
    return tuple(parameters), returned


if __name__ == "__main__":
    ...

    # AI_TASK: I need some examples to run
    # - below are already some temporary helper for the cli output
    # - now I need different Loaders with different Types

    from rich import print
    from rich.panel import Panel
    from rich.text import Text

    def _str(text, /, prefix=True):
        return Text(f"{'str: ' if prefix else ''}{text}")

    def _panel(text, style="cyan", /):
        print(Panel(Text(f"{text}"), style=style))

    def _full(x):
        _panel(repr(x), "green")
        print(f"{len(x)=}")
        print("raw", x)
        print(_str(x))
        print("repr", repr(x))
        for i, y in enumerate(x):
            print(f"item[{i}]", y)
