"""
TAP SPEC

-
                               DependencyLevel.sstcore.port.link[1]
"""

__all__: list[str] = [
    "Channels",
    "LinkSpec",
    "Tap",
]

import os
import typing as _t
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass, field, replace
from functools import wraps
from typing import Any, Generic, Protocol, Self, Unpack

from . import _define as _def
from . import _render
from ._define import LinkInput, PortEmit, PortPrinter

HAND_TOGGLE: tuple[str, ...] = (  # Master PARAM:
    # "log",
    # "report",
    # "init",
    # "name",
)
META_FLAGS: frozenset[str] = frozenset({"log", "report", "init"})
LINK_FLAGS: frozenset[str] = frozenset({"link", "port.link"})


class Channels(frozenset):
    """Guard the active Channels and Rules for Matching"""

    flags: frozenset[str]
    allow_link: bool

    def __new__(cls, env_var="SST_DEBUG", default=()):
        _raw = (*os.getenv(env_var, "").split(","), *default)
        _clean = {c for e in _raw if (c := cls.format(e))}
        unit: Self = super().__new__(cls, _scopes := _clean - META_FLAGS)
        unit.flags = frozenset(_clean & META_FLAGS)
        unit.allow_link = bool(_scopes & LINK_FLAGS)
        return unit

    def __contains__(self, target: Any) -> bool:
        """Matches (class, func, instance, or str) an active scope?"""
        if not self or target is None:
            return False
        key: str = (
            self.format(target) if isinstance(target, str) else self.key(target)
        )
        if ("port.link" in key or key in LINK_FLAGS) and not self.allow_link:
            return False
        if super().__contains__("*"):
            return True
        return any(scope in key for scope in super().__iter__())

    def has_flag(self, flag: str, /) -> bool:
        """Is meta-flag or exact token included?"""
        fmt = self.format(flag)
        return fmt in self.flags or super().__contains__(fmt)

    @classmethod
    def format(cls, target: str, /) -> str:
        return target.strip().lower()

    @classmethod
    def key(cls, target: Any, /) -> str:
        """Lowercased qualified identifier for reliable substring matching"""
        if not isinstance(target, (type, Callable)):
            target = type(target)
        module: str = getattr(target, "__module__", "")
        qualname: str = getattr(
            target, "__qualname__", getattr(target, "__name__", "")
        )
        return f"{module}.{qualname}".lower()


@dataclass(frozen=True, slots=True)
class LinkSpec:
    merge: _def.DocMerging
    channels: Channels = field(init=False)
    theme: _def.DefaultTheme = field(default_factory=_def.DefaultTheme)
    dunders: frozenset[str] = frozenset(_def.DUNDERS)
    skip: frozenset[type] = frozenset({object, Protocol, Generic})

    env_var: str = "SST_DEBUG"
    toggle: tuple[str, ...] = HAND_TOGGLE
    trace_init: bool | None = None
    use_loguru: bool | None = None
    report: int = 0

    def __post_init__(self) -> None:
        ch = Channels(env_var=self.env_var, default=self.toggle)
        object.__setattr__(self, "channels", ch)
        if self.trace_init is None:
            object.__setattr__(self, "trace_init", ch.has_flag("init"))
        if self.use_loguru is None:
            object.__setattr__(self, "use_loguru", ch.has_flag("log"))
        if self.report == 0 and ch.has_flag("report"):
            object.__setattr__(self, "report", 2)

    def update_theme(self, **colors: Unpack[_def.RenderTheme]):
        replace(self.theme, **colors)

    def derive(self, **kwargs: Unpack[LinkInput]) -> Self:
        """Spawn a new isolated LinkSpec with updated fields."""
        if "toggle" in kwargs:
            kwargs["toggle"] = tuple(kwargs["toggle"])
        return replace(self, **kwargs)

    def surface(self, protocol: type) -> list[str]:
        """Generate target Protocol Attrs using '' for the Cls itself"""
        return ["", *_t.get_protocol_members(protocol)]


class Tap:
    """Minimal debug probe for port, brick, and forge bring-up."""

    # LATER: __slots__ = ("_spec", "emit", "printer")

    def __init__(self, spec: LinkSpec, /) -> None:
        self.replace(spec)

    @property
    def spec(self) -> LinkSpec:
        return self._spec

    def replace(self, spec: LinkSpec) -> Self:
        """Swap the underlying frozen LinkSpec and re-bind emit/printer"""
        self._spec = spec
        self.emit: PortEmit = _prepare_emit(spec)
        # Only activate Reflector/Redactor printer if 'report' is on AND 'link' is allowed (or report >= 3)
        self.printer: PortPrinter = (
            _render._load_printer() if spec.report > 0 else _render.NOOP_PRINTER
        )
        return self

    def config(self, **changes: Unpack[LinkInput]) -> Self:
        """Derive new LinkSpec with changes and update Tap in-place"""
        return self.replace(self._spec.derive(**changes))

    def spawn(self, **changes: Unpack[LinkInput]) -> Self:
        """Create an isolated new Tap with a derived LinkSpec"""
        return type(self)(self._spec.derive(**changes))

    def show_result(self, docs: _def.SortedDocs, /) -> None:
        self.printer.show_sort_result(
            docs, level=self._spec.report, **asdict(self._spec.theme)
        )

    def ignores(self, base: type) -> bool:
        return base in self._spec.skip

    @property
    def merge(self) -> _def.DocMerging:
        return self._spec.merge

    @property
    def dunders(self) -> frozenset[str]:
        return self._spec.dunders

    def __bool__(self) -> bool:
        return bool(self._spec.channels)

    def __call__(self, *args: Any, sender: Any = None, **kwargs: Any) -> None:
        self.emit(*args, sender=sender, **kwargs)

    def watches(self, target: Any, /) -> bool:
        return target in self._spec.channels

    def watch[**P, R](self, func: Callable[P, R], /) -> Callable[P, R]:
        """Bind Function or Method at Startup (zero-cost no-op when disabled)"""
        if not self.watches(func):
            return func

        is_method: bool = "." in getattr(func, "__qualname__", "")
        is_init: bool = getattr(func, "__name__", "") in _def.INIT

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

    @_t.overload
    def trace[C](self, cls: type[C], /) -> type[C]: ...
    @_t.overload
    def trace[C](
        self, /, *, methods: Sequence[str] = ()
    ) -> Callable[[type[C]], type[C]]: ...

    def trace[C](
        self, cls: type[C] | None = None, /, *, methods: Sequence[str] = ()
    ) -> type[C] | Callable[[type[C]], type[C]]:
        """Inject self._debug() and wrap target methods"""

        def _decorator(_cls: type[C]) -> type[C]:
            if not _inject_active_debug(self, _cls):
                return _cls
            for method in _dict_hits(_cls, *methods, init=self.spec.trace_init):
                setattr(_cls, method.__name__, self.watch(method))  # ty:ignore
            return _cls

        return _decorator(cls) if cls is not None else _decorator


if _t.TYPE_CHECKING:
    _config: type[_def.LinkConfig] = Tap


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


def _prepare_emit(spec: LinkSpec) -> PortEmit:
    def _emit(*args: Any, sender: Any = None, **kwargs: Any) -> None:
        """Active emission pipeline: Filter sender against spec.channels!"""
        if sender is not None and sender not in spec.channels:
            return

        _render._rich(sender, *args, **kwargs)

        if spec.use_loguru:
            _render._loguru(*args, sender=_who(sender), **kwargs)

    return _emit if spec.channels else _noop


def _unpack(
    func: Callable[..., Any], qual: str, is_method: bool, args: tuple[Any, ...]
) -> tuple[str, Sequence[Any]]:
    """Resolve dynamic method sender and unbound args in one step."""

    if is_method and args:
        target, *unbound = args
        return f"{target}.{func.__name__}", unbound  # ty:ignore

    return qual, args


def _dict_hits(
    cls: type, *attrs: str, init: bool | None = False
) -> list[Callable]:
    """Extract matching callables if present directly from cls.__dict__"""

    methods: list = [cls.__dict__[a] for a in attrs if a in cls.__dict__]

    if init and (_init_ := _dict_hits(cls, *_def.INIT, init=False)):
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
