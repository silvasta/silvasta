"""
TAP SPEC

-
                               DependencyLevel.sstcore.port.link[1]
"""

__all__: list[str] = [
    "LinkSpec",
    "Tap",
]

from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass, field, replace
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol,
    Self,
    Unpack,
    get_protocol_members,
    overload,
)

from . import _render
from ._define import (
    Channels,
    DefaultTheme,
    DocMerging,
    LinkConfig,
    LinkInput,
    PortEmit,
    PortPrinter,
    RenderTheme,
    SortedDocs,
)

HAND_TOGGLE: tuple[str, ...] = (
    "color",
    "vault",
    "init",
)

DUNDERS: set[str] = {
    "__doc__",
    "__func__",
    "__portlinks__",
}


@dataclass
class LinkSpec:
    merge: DocMerging
    channels: Channels = field(init=False, repr=False)
    emit: PortEmit = field(init=False, repr=False)
    printer: PortPrinter = field(init=False, repr=False)
    #
    env_var: str = "SST_DEBUG"
    toggle: tuple[str, ...] = HAND_TOGGLE
    trace_init: bool | None = None
    use_loguru: bool | None = None
    report: int = 0
    theme: DefaultTheme = DefaultTheme()
    dunders: frozenset[str] = frozenset(DUNDERS)
    skip: frozenset[type] = frozenset({object, Protocol, Generic})

    def __post_init__(self) -> None:
        self._sync()

    def _sync(self) -> None:
        """Synthesize channels, emitter, and printer from current config fields."""
        self.channels = Channels(env_var=self.env_var, default=self.toggle)

        if self.trace_init is None:
            self.trace_init: bool = self.channels.has("init")
        if self.use_loguru is None:
            self.use_loguru: bool = self.channels.has("log")
        if self.report == 0 and self.channels.has("report"):
            self.report = 2

        self.emit: PortEmit = _prepare_emit(self)
        self.printer: PortPrinter = (
            _render._load_printer() if self.report > 0 else _render.NOOP_PRINTER
        )

    def configure(self, **kwargs: Unpack[LinkInput]) -> Self:
        # LATER: clean this up
        """Mutate this LinkSpec in-place and re-synthesize runtime pipelines."""
        for k, v in kwargs.items():
            if not hasattr(self, k):
                raise AttributeError(f"Unknown LinkSpec option: {k!r}")
            if k == "toggle":
                v = tuple(v)  # ty:ignore
            setattr(self, k, v)
        self._sync()
        return self

    def show_result(self, docs: SortedDocs, /):
        self.printer.show_sort_result(
            docs, level=self.report, **asdict(self.theme)
        )

    def update_theme(self, **colors: Unpack[RenderTheme]):
        replace(self.theme, **colors)

    def derive(self, **kwargs: Unpack[LinkInput]) -> Self:
        """Spawn a new isolated LinkSpec with updated fields."""
        if "toggle" in kwargs:
            kwargs["toggle"] = tuple(kwargs["toggle"])
        return replace(self, **kwargs)

    def ignores(self, base: type) -> bool:
        return base in self.skip

    def surface(self, protocol: type) -> list[str]:
        """Generate target Protocol Attrs using '' for the Cls itself"""
        return ["", *get_protocol_members(protocol)]


if TYPE_CHECKING:
    _: type[LinkConfig] = LinkSpec


class Tap:
    """Minimal debug probe for port, brick, and forge bring-up."""

    # AI: this feels more like a heavy penality for not even a minimal gain
    # __slots__ = ("channels", "trace_init", "use_loguru", "emit")

    def __init__(self, spec: LinkSpec):
        """Bind once at startup: zero branching overhead when OFF"""
        self.spec: LinkSpec = spec

    def __bool__(self) -> bool:
        return bool(self.spec.channels)

    def __call__(self, *args: Any, sender: Any = None, **kwargs: Any) -> None:
        self.spec.emit(*args, sender=sender, **kwargs)

    def watches(self, target: Any, /) -> bool:
        return target in self.spec.channels

    def watch[**P, R](self, func: Callable[P, R], /) -> Callable[P, R]:
        """Bind Function or Method at Startup (zero-cost no-op when disabled)"""
        if not self.watches(func):
            return func

        is_method: bool = "." in getattr(func, "__qualname__", "")
        is_init: bool = getattr(func, "__name__", "") in INIT

        @wraps(func)
        def _traced(*args: P.args, **kwargs: P.kwargs) -> R:
            result: R = func(*args, **kwargs)  # before _unpack!
            sender, _args = _unpack(func, Channels.key(func), is_method, args)
            self.spec.emit(f"Params: {_args=} {kwargs=}", sender=sender)
            message = (
                f"Created -> {args[0]!r}" if is_init else f"Result: {result!r}"
            )
            self.spec.emit(message, sender=sender)
            return result

        return _traced

    @overload
    def trace[C](self, cls: type[C], /) -> type[C]: ...
    @overload
    def trace[C](
        self, /, *, methods: Sequence[str] = ()
    ) -> Callable[[type[C]], type[C]]: ...

    def trace[C](
        self, cls: type[C] | None = None, /, *, methods: Sequence[str] = ()
    ) -> type[C] | Callable[[type[C]], type[C]]:
        """Inject self._debug() and wrap target methods on a class."""

        def _decorator(_cls: type[C]) -> type[C]:
            if not _inject_active_debug(self, _cls):
                return _cls
            for method in _dict_hits(_cls, *methods, init=self.spec.trace_init):
                setattr(_cls, method.__name__, self.watch(method))  # ty:ignore
            return _cls

        return _decorator(cls) if cls is not None else _decorator


def _noop(*_: Any, **__: Any) -> None:
    """Zero-cost sink when debug is disabled."""


def _inject_active_debug(tap: Tap, cls: type) -> bool:
    def _debug(self, *args, **kwargs):
        """Inject this to cls"""
        tap.spec.emit(*args, sender=self, **kwargs)

    active: bool = bool(tap) and tap.watches(cls)
    if not hasattr(cls, "_debug"):
        cls._debug = _debug if active else _noop  # ty:ignore
    return active


def _prepare_emit(spec: LinkSpec):
    def _emit(*args: Any, sender: Any = None, **kwargs: Any) -> None:
        """Active emission pipeline (only bound when CHANNELS is non-empty)."""
        sender: str = _who(sender)
        _render._rich(sender, *args, **kwargs)
        if spec.use_loguru:
            _render._loguru(*args, sender, **kwargs)

    return _emit if spec.channels else _noop


def _unpack(
    func: Callable[..., Any], qual: str, is_method: bool, args: tuple[Any, ...]
) -> tuple[str, Sequence[Any]]:
    """Resolve dynamic method sender and unbound args in one step."""

    if is_method and args:
        target, *unbound = args
        return f"{_who(target)}.{func.__name__}", unbound  # ty:ignore

    return qual, args


INIT = ("__post_init__", "__init__")


def _dict_hits(
    cls: type, *attrs: str, init: bool | None = False
) -> list[Callable]:
    """Extract matching callables if present directly from cls.__dict__"""

    methods: list = [cls.__dict__[a] for a in attrs if a in cls.__dict__]

    if init and (_init_ := _dict_hits(cls, *INIT, init=False)):
        methods.append(_init_[0])  # prefers __post_init__ if exists

    return methods


def _who(target: Any, /) -> str:
    """Format a readable sender label for instances, classes, or strings."""
    if target is None:
        return ""
    if isinstance(target, str):
        return target
    if isinstance(target, type):
        return target.__name__
    return str(target)
