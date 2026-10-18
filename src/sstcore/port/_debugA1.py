# sstcore/port/_debug.py
import os
from collections.abc import Callable
from functools import wraps
from typing import Any

ACTIVE_SCOPES: set[str] = set(
    filter(None, os.getenv("SST_DEBUG", "color,vault").split(","))
)


def is_active(module_or_name: str = "*") -> bool:
    if not ACTIVE_SCOPES:
        return False
    if "*" in ACTIVE_SCOPES:
        return True
    return any(scope in module_or_name.lower() for scope in ACTIVE_SCOPES)


def _noop(*_args: Any, **_kwargs: Any) -> None:
    pass


class MiniProbe:
    """Zero-dependency inner-core debug probe."""

    def __init__(self) -> None:
        self.enabled: bool = bool(ACTIVE_SCOPES)
        # Bind once at startup! No `if` check per call when disabled.
        self.emit: Callable[..., None] = (
            self._rich_emit if self.enabled else _noop
        )

    def _rich_emit(
        self, *args: Any, sender: Any = None, tag: str = "", **kwargs: Any
    ) -> None:
        from rich import print as rprint

        if sender is not None:
            cls_name = (
                sender.__name__
                if isinstance(sender, type)
                else type(sender).__name__
            )
            mod_name = getattr(sender, "__module__", "")
            if not is_active(f"{mod_name}.{cls_name}.{tag}"):
                return
            prefix = f"[bold cyan]{cls_name}[/]" + (
                f"[dim].{tag}[/]" if tag else ""
            )
            rprint(f"⚡ {prefix} │", *args, **kwargs)
        else:
            rprint("⚡", *args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        self.emit(*args, **kwargs)


tap = MiniProbe()


class _PortLink:
    def __call__[C, P](self, protocol: type[P], /):
        """Merge docstrings and enforce static type check"""

        def portlinker(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)
            """Catch all __doc__ merge issues and always return original Cls"""

            # NOTE:
            if tap.enabled and is_active(cls.__module__):
                # 1. Inject bound _emit so any method on `cls` can call `self._emit(...)`
                if not hasattr(cls, "_emit"):
                    cls._emit = lambda self, *a, **kw: tap.emit(
                        *a, sender=self, **kw
                    )

                # 2. Optional: Auto-trace __init__ creation if "init" is in ACTIVE_SCOPES
                if "init" in ACTIVE_SCOPES and "__init__" in cls.__dict__:
                    orig_init = cls.__init__

                    @wraps(orig_init)
                    def _tracked_init(self, *a, **kw):
                        orig_init(self, *a, **kw)
                        tap.emit(
                            f"Created -> {self!r}", sender=self, tag="__init__"
                        )

                    cls.__init__ = _tracked_init
            # NOTE:

            return cls

        return portlinker


def fn(func: Callable) -> Callable:
    """Zero-cost decorator when disabled; logs args -> return when active."""
    if not tap.enabled or not is_active(
        f"{func.__module__}.{func.__qualname__}"
    ):
        return func  # <- Literal no-op at import time!

    @wraps(func)
    def _wrapper(*args: Any, **kwargs: Any) -> Any:
        sender = args[0] if args else func.__qualname__
        tap.emit(
            f"in: {args[1:]!r} {kwargs or ''}",
            sender=sender,
            tag=func.__name__,
        )
        res = func(*args, **kwargs)
        tap.emit(f"out: {res!r}", sender=sender, tag=func.__name__)
        return res

    return _wrapper
