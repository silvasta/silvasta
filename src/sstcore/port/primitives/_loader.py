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
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from inspect import Signature, signature
from typing import Any, Literal, Self, TypedDict

from ..empty import VOID, MayBe, MayNot
from . import _typearg
from ._typearg import extract_type_args, format_type_arg


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

    @property
    def value(self) -> T:
        """Provide the loaded Value or Raise"""
        if self._value is not VOID:
            return self._value
        raise LookupError(f"{self!r} has neither a callable nor a default")

    @property
    def is_ready(self) -> bool:
        return self._value is not VOID

    def __init__(
        self,
        func: MayNot[LoadFunc[P, T]] = None,
        /,
        **tkw: _t.Unpack[LoaderInput[T]],
    ):
        """So far no check if Loader can complete, use Loader.__bool__"""
        self._func: MayNot[LoadFunc[P, T]] = func
        self._default: MayBe[T] = tkw.get("default", VOID)
        self._prefer: Prefer = tkw.get("prefer", "func")

        self._counter: int = 0
        self._total_counter: int = 0
        self._value: MayBe[T] = VOID

    def bind(self, fn: Callable[P, T]) -> Callable[P, T]:
        """Attach or replace the loader callable and reset execution state"""
        self._func: LoadFunc[P, T] = fn
        self.reset()
        return fn

    def clone(self) -> Self:
        """Copy same Configuration but with fresh State and Value"""
        return type(self)(
            self._func, default=self._default, prefer=self._prefer
        )

    @classmethod
    def loading(
        cls, loading: MayNot[Loading[P, T]], /, **tkw: _t.Unpack[LoaderInput[T]]
    ) -> Self:
        """Create from existing loader, function or just from kwargs"""
        return (
            loading.clone().updated(**tkw)  # ty:ignore
            if isinstance(loading, Loader)
            else cls(loading, **tkw)
        )

    def updated(self, **tkw: _t.Unpack[LoaderInput[T]]) -> Self:
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
        # NOTE: latest when 3 dispatches occur... it will be difficult
        loaders: list[LoadFunc] = [
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
    specs = extract_type_args(loader) if _looks_generic(loader) else ()
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
    # MOVE: create new module outside library in examples/...

    def main():
        # test_1()
        test_2()
        pass

    from rich import print
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    def test_1():

        def _inspect(name: str, loader: Loader[Any, Any]) -> None:
            lines = [
                f"str:   {loader}",
                f"repr:  {loader!r}",
                f"type:  {loader.target_type!r} (via {loader.type_args.value_source})",
                f"specs: {[str(s) for s in loader.type_args.specs]}",
            ]
            print(
                Panel(Text("\n".join(lines)), title=name, border_style="cyan")
            )

        l_empty = Loader()
        l_default = Loader(default=42)
        l_none = Loader(default=None)

        l_explicit = Loader[[str, int], float]()
        l_ellipsis = Loader[..., list[str]]()

        def fetch(host: str, port: int) -> dict[str, Any]:
            return {"host": host, "port": port}

        l_func = Loader(fetch)
        l_func_loaded = Loader(fetch)
        l_func_loaded("localhost", 8080)

        class IntLoader[**P](Loader[P, int]): ...

        class ZeroArgIntLoader(IntLoader[[]]): ...

        class GenericBoxLoader[T](Loader[[T], list[T]]): ...

        class StrBoxLoader(GenericBoxLoader[str]): ...

        class UnboundLoader[T](Loader[[int], T]): ...

        examples: list[tuple[str, Loader[Any, Any]]] = [
            ("Empty", l_empty),
            ("Default int", l_default),
            ("Default None", l_none),
            ("Explicit [[str, int], float]", l_explicit),
            ("Explicit [..., list[str]]", l_ellipsis),
            ("Typed func (unloaded)", l_func),
            ("Typed func (loaded)", l_func_loaded),
            ("Subclass IntLoader", IntLoader()),
            ("Subclass ZeroArgIntLoader", ZeroArgIntLoader()),
            ("Multi-level StrBoxLoader", StrBoxLoader()),
            ("Unbound GenericBoxLoader", GenericBoxLoader()),
            ("UnboundLoader[T]", UnboundLoader()),
        ]

        for label, ldr in examples:
            _inspect(label, ldr)

    def test_2():

        def _str(text: object, /, prefix: bool = True) -> Text:
            return Text(f"{'str: ' if prefix else ''}{text}")

        def _panel(text: object, style: str = "cyan", /) -> None:
            print(Panel(Text(str(text)), style=style))

        def _full(items: tuple[object, ...], /) -> None:
            _panel(repr(items), "green")
            print(f"{len(items)=}")
            print(_str(items))
            for index, item in enumerate(items):
                print(f"item[{index}]", item)

        def load_str() -> str:
            return "loaded"

        def load_int(n: int) -> int:
            return n

        def load_union() -> int | str:
            return 1

        class IntLoader(Loader[..., int]): ...

        class SubIntLoader(IntLoader): ...

        class OpenLoader[X](Loader[..., X]): ...

        class ListLoader[X](Loader[..., list[X]]): ...

        class IntListLoader(ListLoader[int]): ...

        class PairLoader(Loader[[int, str], bool]): ...

        ready = Loader(load_str)
        ready()
        held = Loader(load_int, default=0, prefer="default")
        held(4)

        samples = (
            ("bare", Loader()),
            ("subscript", Loader[..., int]()),
            ("int subclass", IntLoader()),
            ("deep subclass", SubIntLoader()),
            ("open", OpenLoader()),
            ("open + default", OpenLoader(default=5)),
            ("substituted", IntListLoader()),
            ("param list", PairLoader()),
            ("default", Loader(default=5)),
            ("default none", Loader(default=None)),
            ("default bool", Loader(default=True)),
            ("func", Loader(load_str)),
            ("func args", Loader(load_int)),
            ("union func", Loader(load_union)),
            ("func beats default", Loader(load_str, default=5)),
            ("explicit beats both", IntLoader(load_str, default="nope")),  # ty:ignore
            ("loaded", ready),
            ("prefer default", held),
        )

        _panel("loader spectrum")
        table = Table(show_lines=True)
        for column in ("case", "str", "T", "T from", "P", "P from", "also"):
            table.add_column(column)
        for case, loader in samples:
            found = loader.type_args
            extra = []
            if found.func_return is not VOID:
                extra.append(f"func={format_type_arg(found.func_return)}")
            if found.default_type is not VOID:
                extra.append(f"default={format_type_arg(found.default_type)}")
            table.add_row(
                case,
                str(loader),
                format_type_arg(found.value),
                found.value_source,
                _typearg.format_parameters(found.parameters),
                found.parameters_source,
                ", ".join(extra) or "-",
            )
        print(table)

        _panel("IntListLoader bases, after substitution")
        _full(extract_type_args(IntListLoader()))

        _panel("OpenLoader, X stays open")
        _full(extract_type_args(OpenLoader()))

    main()
