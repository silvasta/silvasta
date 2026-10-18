# /home/silvan/sstcore/src/sstcore/port/_debug.py
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
    "MiniProbe",
]


import os
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from types import SimpleNamespace
from typing import Any, Generic, Protocol

from .link._define import DocMerger, PortEmit, PortLinker

TOGGLE: str = "color,vault,init"

_RAW_SCOPES: str = os.getenv("SST_DEBUG", TOGGLE)
ACTIVE_SCOPES: frozenset[str] = frozenset(
    s.strip().lower() for s in _RAW_SCOPES.split(",") if s.strip()
)


def _noop(*_args: Any, **_kwargs: Any) -> None:
    """Zero-cost sink when debug is disabled."""


class MiniProbe:
    """Minimal debug probe for port, brick, and forge bring-up."""

    __slots__ = ("enabled", "trace_init", "use_loguru", "emit")

    def __init__(self) -> None:
        self.enabled: bool = bool(ACTIVE_SCOPES)
        self.trace_init: bool = "init" in ACTIVE_SCOPES
        self.use_loguru: bool = "log" in ACTIVE_SCOPES
        # Bind once at startup: zero branching overhead when OFF
        self.emit: Callable[..., None] = (
            self._active_emit if self.enabled else _noop
        )

    def __bool__(self) -> bool:
        return self.enabled

    def __call__(
        self, *args: Any, sender: Any = None, tag: str = "", **kwargs: Any
    ) -> None:
        self.emit(*args, sender=sender, tag=tag, **kwargs)

    def matches(self, target: str) -> bool:
        """Check if a module/class/tag path matches active scopes."""
        if not self.enabled:
            return False
        low = target.lower()
        # Prevent PortLink's internal MRO walking from flooding every run
        # unless "link" is explicitly requested in TOGGLE
        if "port.link" in low and "link" not in ACTIVE_SCOPES:
            return False
        if "*" in ACTIVE_SCOPES:
            return True
        return any(scope in low for scope in ACTIVE_SCOPES)

    def _active_emit(
        self, *args: Any, sender: Any = None, tag: str = "", **kwargs: Any
    ) -> None:
        from rich import print as rprint

        if sender is not None:
            is_cls = isinstance(sender, type)
            cls_name = sender.__name__ if is_cls else type(sender).__name__
            mod_name = getattr(sender, "__module__", "")
            if not self.matches(f"{mod_name}.{cls_name}.{tag}"):
                return

            # Render sender using its own __rich__ / __str__ if it's an instance
            who = (
                f"[bold cyan]{cls_name}[/]"
                if is_cls
                else f"[bold cyan]{sender}[/]"
            )
            sfx = f"[dim].{tag}[/]" if tag else ""
            rprint(f"[dim]⚡[/]{who}{sfx} [dim]│[/]", *args, **kwargs)
        else:
            if tag and not self.matches(tag):
                return
            sfx = f"[bold yellow]{tag}[/] [dim]│[/] " if tag else ""
            rprint(f"[dim]⚡[/]{sfx}", *args, **kwargs)

        if self.use_loguru:
            from loguru import logger

            msg = " ".join(
                repr(a) if not isinstance(a, str) else a for a in args
            )
            logger.opt(depth=2).debug(f"[{sender or tag}] {msg}")

    # ── Decorators & Class Injection ─────────────────────────────────────────

    def fn[F: Callable[..., Any]](self, func: F) -> F:
        """Startup-bound function decorator: zero-cost no-op when disabled."""
        qual = f"{func.__module__}.{func.__qualname__}"
        if not self.matches(qual):
            return func

        @wraps(func)
        def _traced(*args: Any, **kwargs: Any) -> Any:
            sender = args[0] if args else None
            self._active_emit(
                f"in:  args={args[1:]!r} kwargs={kwargs or '{}'}",
                sender=sender,
                tag=func.__name__,
            )
            res = func(*args, **kwargs)
            self._active_emit(
                f"out: {res!r}",
                sender=sender,
                tag=func.__name__,
            )
            return res

        return _traced  # type: ignore[return-value]

    def hook_class[C](self, cls: type[C]) -> type[C]:
        """Inject self._debug() and optional __init__ tracing into a class."""
        # Always attach _debug so inline `self._debug(...)` never raises AttributeError
        if not hasattr(cls, "_debug"):
            if self.enabled and self.matches(
                f"{cls.__module__}.{cls.__qualname__}"
            ):
                cls._debug = lambda self, *a, **kw: tap.emit(  # type: ignore[attr-defined]
                    *a, sender=self, **kw
                )
            else:
                cls._debug = _noop  # type: ignore[attr-defined]

        if not (
            self.enabled
            and self.trace_init
            and self.matches(f"{cls.__module__}.{cls.__qualname__}")
        ):
            return cls

        # Hook __post_init__ (for @dataclass like PaletteDTO) or __init__
        hook_name = (
            "__post_init__" if "__post_init__" in cls.__dict__ else "__init__"
        )
        if hook_name in cls.__dict__:
            orig = cls.__dict__[hook_name]

            @wraps(orig)
            def _wrapped_init(self: Any, *args: Any, **kwargs: Any) -> Any:
                res = orig(self, *args, **kwargs)
                tap._active_emit(
                    f"Created -> {self!r}", sender=self, tag=hook_name
                )
                return res

            setattr(cls, hook_name, _wrapped_init)

        return cls


tap = MiniProbe()


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# /home/silvan/sstcore/src/sstcore/port/link/_define.py
# ... existing imports ...


@dataclass(frozen=True, slots=True)
class LinkSpec:
    skip: frozenset[type] = frozenset({object, Protocol, Generic})
    on_exit_with_error: bool = True
    merge: DocMerger = lambda docs: f"merge: {docs}"
    # NEXT:
    emit: PortEmit | None = tap.emit  # <-- Wired directly to MiniProbe


# /home/silvan/sstcore/src/sstcore/port/link/_operator.py
# ... existing imports ...


class EasyNote(SimpleNamespace):
    """Stable Base for all Easy Member"""

    _emit: Callable | None = None

    def emit(self, *args, **kwargs):
        (self._emit or self.port_emit)(*args, sender=self, **kwargs)

    @staticmethod
    def port_emit(*args, **kwargs):
        tap.emit(*args, **kwargs)

    def __str__(self):
        return f"{type(self).__name__}"


class _P:
    def __call__[C, P](self, protocol: type[P], /) -> PortLinker[C, P]:
        """Merge docstrings and enforce static type check"""

        def portlinker(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)
            """Catch all __doc__ merge issues and always return original Cls"""

            # INFO: all operations

            return tap.hook_class(cls)  # <-- Injects _debug and init tracing

        return portlinker
