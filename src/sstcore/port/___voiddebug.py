"""
Minimal Inner-Core Debug Engine (DependencyLevel[0])

- Single point of control via TOGGLE or SST_DEBUG env variable
- Zero runtime overhead when disabled (resolves at import time)
- Lazy rich / loguru binding to prevent circular imports in port/brick/forge


1-PLACE MANUAL TOGGLE:

Examples:
  ""                   -> Completely OFF (zero runtime overhead)
  "*"                  -> Everything ON (excluding 'link' unless specified)
  "color,vault"        -> Only modules/classes matching 'color' or 'vault'
  "color,vault,init"   -> Also auto-print __init__ / __post_init__ creations
  "link"               -> Include PortOperator / EasyNote MRO pipeline logs

"""

__all__: list[str] = [
    "tap",
    "Tap",
]


import os
from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, Protocol, overload

from .empty import VOID, MayBe

TOGGLE: str = "color,vault,init"  # PARAM: turn this off later == ""

CHANNELS: frozenset[str] = frozenset(
    s.strip().lower()
    for s in os.getenv(key="SST_DEBUG", default=TOGGLE).split(",")
    if s.strip()
)


class PortEmit[**P](Protocol):
    def __call__(
        self,
        *args,
        sender: Any = None,
        tag: str = "",  # REMOVE:??
        **kwargs,
    ) -> None: ...


class Tap:
    """Minimal debug probe for port, brick, and forge bring-up."""

    __slots__ = ("enabled", "trace_init", "use_loguru", "emit")

    def __init__(self) -> None:
        self.enabled: bool = bool(CHANNELS)
        self.trace_init: bool = "init" in CHANNELS
        self.use_loguru: bool = "log" in CHANNELS
        # Bind once at startup: zero branching overhead when OFF
        self.emit: PortEmit = _emit if self.enabled else _noop

    def __bool__(self) -> bool:
        return self.enabled

    def __call__(
        self, *args: Any, sender: Any = None, tag: str = "", **kwargs: Any
    ) -> None:
        self.emit(*args, sender=sender, tag=tag, **kwargs)

    def matches(self, target: str, /) -> bool:
        # NEXT: check link._dunder
        """Check if a module/class/tag path matches active scopes."""
        if not self.enabled:
            return False
        if "port.link" in target and "link" not in CHANNELS:
            return False
        if "*" in CHANNELS:
            return True
        return any(scope in target for scope in CHANNELS)

    def fn[**P, R](self, func: Callable[P, R]) -> Callable[P, R]:
        """Startup-bound function decorator: zero-cost no-op when disabled."""

        if not self.matches(qual := _qual(func)):
            return func

        is_method: bool = "." in func.__qualname__

        @wraps(func)
        def _traced(*args: P.args, **kwargs: P.kwargs) -> R:

            if is_method and args:
                _target, *_unbound = args  # AI: does this work?
                # target, unbound = args[0], args[1:]
                sender: Any = f"{_who(_target)}.{func.__name__}"  # LATER: chech __qualname__
            else:
                _unbound = args
                sender = qual

            self.emit(
                f"params: args={_unbound!r} kwargs={kwargs or '{}'}",
                sender=sender,
            )
            result: R = func(*args, **kwargs)
            self.emit(f"result: {result!r}", sender=sender)

            return result

        return _traced

    def _hook_class[C](self, cls: type[C]) -> type[C]:
        if not hasattr(cls, "_debug"):
            cls._debug = (  # ty:ignore
                _debug if self.enabled and self.matches(_qual(cls)) else _noop
            )
        if not (self.enabled and self.trace_init and self.matches(_qual(cls))):
            return cls
        # EXTRACT:
        # EXTRACT:
        # EXTRACT:
        method_to_bind: MayBe = ___dict(cls, "__post_init__", "__init__")
        if method_to_bind is VOID:
            return cls
        # EXTRACT:
        # EXTRACT:

        @wraps(wrapped=method_to_bind)
        def _wrapped_init(self: Any, *args: Any, **kwargs: Any) -> Any:
            res: Any = method_to_bind(self, *args, **kwargs)
            tap.emit(  # CHECK: why tap? why _active_emit?
                f"Created -> {self!r}",
                sender=self,
                tag=method_to_bind.__name__,
            )
            return res

        setattr(cls, method_to_bind.__name__, _wrapped_init)
        return cls

    @overload
    def hook_class[C](self, cls: type[C], /) -> type[C]: ...
    @overload
    def hook_class[C](
        self, /, *, methods: Sequence[str] = ()
    ) -> Callable[[type[C]], type[C]]: ...

    def hook_class[C](
        self,
        cls: type[C] | None = None,
        /,
        *,
        methods: Sequence[str] = ("__post_init__", "__init__"),
    ) -> type[C] | Callable[[type[C]], type[C]]:
        """Inject self._debug() and wrap target methods on a class."""

        def _decorator(target_cls: type[C]) -> type[C]:
            active: bool = self.enabled and self.matches(_qual(target_cls))

            if not hasattr(target_cls, "_debug"):
                target_cls._debug = _debug if active else _noop  # ty:ignore

            if not (active and self.trace_init):
                return target_cls

            for method in _dict_hits(target_cls, *methods):
                setattr(target_cls, method.__name__, self._wrap_init(method))

            return target_cls

        return _decorator(cls) if cls is not None else _decorator

    def _wrap_init(self, method: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(wrapped=method)
        def _wrapped(instance: Any, *args: Any, **kwargs: Any) -> Any:
            # AI: what is the difference to _traced?
            res: Any = method(instance, *args, **kwargs)
            self.emit(
                f"Created -> {instance!r}",
                sender=f"{_who(instance)}.{method.__name__}",
            )
            return res

        return _wrapped


tap = Tap()  # TARGET: main result


def _noop(*_args: Any, **_kwargs: Any) -> None:
    """Zero-cost sink when debug is disabled."""


def _emit(*args: Any, sender: Any = None, **kwargs: Any) -> None:
    """Active emission pipeline (only bound when CHANNELS is non-empty)."""
    if sender is not None and not isinstance(sender, str):
        if not tap.matches(_qual(sender)):
            return
    prefix: str = f"[bold cyan]{_who(sender)}[/] [dim]│[/]" if sender else ""
    _render_rich(prefix, *args, **kwargs)
    if tap.use_loguru:
        _render_log(sender, *args)


def _debug(self, *args, **kwargs):
    """Inject to cls"""
    tap.emit(*args, sender=self, **kwargs)


#  LINE: -- Output -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _render_rich(prefix: str, *args: Any, **kwargs: Any) -> None:
    from rich import print as rprint

    rprint(f"[dim]⚡[/]{prefix}", *args, **kwargs)


def _render_log(sender: Any, *args: Any) -> None:
    from loguru import logger

    msg = " ".join(repr(a) if not isinstance(a, str) else a for a in args)
    logger.opt(depth=3).debug(f"[{_who(sender)}] {msg}")


#  LINE: -- Helper -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _dict_hits(cls: type, *attrs: str) -> list[Callable[..., Any]]:
    """Extract matching callables present directly in cls.__dict__."""
    # TODO:
    if attrs == ("__post_init__", "__init__"):
        for attr in attrs:
            if attr in cls.__dict__:
                return [cls.__dict__[attr]]
        return []
    return [cls.__dict__[a] for a in attrs if a in cls.__dict__]


def ___dict(cls, *attrs: str) -> Any | VOID:
    """Extract first hit of attr in __dict__"""
    # EXTRACT:
    # EXTRACT:
    # EXTRACT:
    for attr in attrs:
        if attr in cls.__dict__:
            return cls.__dict__[attr]
    return VOID


def _who(target: Any, /) -> str:
    """Format a readable sender label for instances, classes, or strings."""
    if target is None:
        return ""
    if isinstance(target, str):
        return target
    if isinstance(target, type):
        return target.__name__
    return str(target)


def _qual(target: Any, /) -> str:
    """Generate full module.qualname path for scope matching."""
    mod = getattr(target, "__module__", "")
    qual = getattr(
        target, "__qualname__", getattr(type(target), "__qualname__", "")
    )
    return f"{mod}.{qual}"


def ___qual(target, /) -> str:
    """Generate name for matching and identification"""
    return f"{target.__module__}.{target.__qualname__}"
