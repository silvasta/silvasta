"""
TAP SPEC

-
                               DependencyLevel.sstcore.port.link[1]
"""

__all__: list[str] = [
    "LinkSpec",
    "Tap",
]

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, replace
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol,
    Self,
    get_protocol_members,
    overload,
)

from . import _render
from ._define import Channels, DocMerging, PortEmit, PortPrinter

HAND_TOGGLE: tuple[str, ...] = (
    # AI: this below are module names (and __init__),
    # impossible to get a direct hint from that for emit or printer
    "color",
    "vault",
    "init",
)
INIT = ("__post_init__", "__init__")

#  LINE: -- The final Config?? -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LinkConfig(Protocol):  # MOVE: to _define when finished
    """The Part intended for separated mutable dataclass"""

    @property
    def emit(self) -> PortEmit: ...
    @property
    def printer(self) -> PortPrinter: ...
    def ignores(self, base: type) -> bool: ...


@dataclass(frozen=True, slots=True)
class LinkSpec:
    emit: PortEmit
    printer: PortPrinter
    merge: DocMerging
    skip: frozenset[type] = frozenset({object, Protocol, Generic})
    # CHECK: dunders

    def ignores(self, base: type) -> bool:
        return base in self.skip

    def derive(self, **kwargs) -> Self:
        # TODO: when setup clear:
        # **kwargs:Unpack[LinkInput] or similar, or just hardcode forward param
        return replace(self, **kwargs)

    def surface(self, protocol: type) -> list[str]:
        """Generate target Protocol Attrs using '' for the Cls itself"""
        return ["", *get_protocol_members(protocol)]

    def configure(self, **kwargs: Any) -> Self:
        """Mutate this LinkSpec in-place for global project-wide changes."""
        for k, v in kwargs.items():
            if not hasattr(self, k):
                raise AttributeError(f"Unknown LinkSpec option: {k!r}")
            setattr(self, k, v)
        return self


if TYPE_CHECKING:
    _: type[LinkConfig] = LinkSpec


class Tap:
    """Minimal debug probe for port, brick, and forge bring-up."""

    # AI: this feels more like a heavy penality for not even a minimal gain
    # __slots__ = ("channels", "trace_init", "use_loguru", "emit")

    def __init__(
        self, env_var: str = "SST_DEBUG", toggle: Iterable[str] = HAND_TOGGLE
    ):
        """Bind once at startup: zero branching overhead when OFF"""
        self.configure(env_var=env_var, toggle=toggle)

    def configure(
        self, env_var: str = "SST_DEBUG", toggle: Iterable[str] = ()
    ) -> Self:
        """Mutate Tap state in-place so all downstream imports see the new rules."""

        self.channels = Channels(env_var=env_var, default=tuple(toggle))
        self.trace_init: bool = self.channels.has("init")
        self.use_loguru: bool = self.channels.has("log")
        self.emit: PortEmit = _prepare_emit(self)
        self.printer: PortPrinter = (
            _render._load_printer()
            if self.channels.has(
                "color"
            )  # FAIL: running brick.color together with printer is like 1000 prints per second...
            else _render.NOOP_PRINTER
        )  # IDEA: use spec here inside as well! some basic config with a lot of options
        # NEXT: printer:on/off is even one of the important,
        # sumarizing over any color setup it will end in some json,
        # for cli-control maybe some InfFlag, or trigger empty-json write
        return self

    def __bool__(self) -> bool:
        return bool(self.channels)

    def __call__(self, *args: Any, sender: Any = None, **kwargs: Any) -> None:
        self.emit(*args, sender=sender, **kwargs)

    def watches(self, target: Any, /) -> bool:
        return target in self.channels

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
            self.emit(f"Params: {_args=} {kwargs=}", sender=sender)
            message = (
                f"Created -> {args[0]!r}" if is_init else f"Result: {result!r}"
            )
            self.emit(message, sender=sender)
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
            for method in _dict_hits(_cls, *methods, init=self.trace_init):
                setattr(_cls, method.__name__, self.watch(method))  # ty:ignore
            return _cls

        return _decorator(cls) if cls is not None else _decorator


def _noop(*_: Any, **__: Any) -> None:
    """Zero-cost sink when debug is disabled."""


def _inject_active_debug(tap: Tap, cls: type) -> bool:
    def _debug(self, *args, **kwargs):
        """Inject this to cls"""
        tap.emit(*args, sender=self, **kwargs)

    active: bool = bool(tap) and tap.watches(cls)
    if not hasattr(cls, "_debug"):
        cls._debug = _debug if active else _noop  # ty:ignore
    return active


def _prepare_emit(tap: Tap):
    def _emit(*args: Any, sender: Any = None, **kwargs: Any) -> None:
        """Active emission pipeline (only bound when CHANNELS is non-empty)."""
        sender: str = _who(sender)
        _render._rich(sender, *args, **kwargs)
        if tap.use_loguru:
            _render._loguru(*args, sender, **kwargs)

    return _emit if bool(tap) else _noop  # AI: is bool(..) here needed?


def _unpack(
    func: Callable[..., Any], qual: str, is_method: bool, args: tuple[Any, ...]
) -> tuple[str, Sequence[Any]]:
    """Resolve dynamic method sender and unbound args in one step."""

    if is_method and args:
        target, *unbound = args
        return f"{_who(target)}.{func.__name__}", unbound  # ty:ignore

    return qual, args


def _dict_hits(cls: type, *attrs: str, init: bool = False) -> list[Callable]:
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
