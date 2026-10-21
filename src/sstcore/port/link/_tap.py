"""
Minimal Inner-Core Debug Engine (DependencyLevel[0])

- Single point of control via TOGGLE or SST_DEBUG env variable
- Zero runtime overhead when disabled (resolves at import time)
- Lazy rich / loguru binding to prevent circular imports in port/brick/forge

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


from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, overload

from ._define import PortEmit
from ._storage import Channels

TOGGLE: tuple[str, ...] = (
    "color",
    "vault",
    "init",
)
CHANNELS = Channels(env_var="SST_DEBUG", default=TOGGLE)

INIT = ("__post_init__", "__init__")


class Tap:
    """Minimal debug probe for port, brick, and forge bring-up."""

    __slots__ = ("enabled", "trace_init", "use_loguru", "emit")

    def __init__(self) -> None:
        """Bind once at startup: zero branching overhead when OFF"""
        self.enabled: bool = bool(CHANNELS)
        self.trace_init: bool = CHANNELS.has("init")
        self.use_loguru: bool = CHANNELS.has("log")
        self.emit: PortEmit = _emit if self.enabled else _noop

    def __bool__(self) -> bool:
        return self.enabled

    def __call__(self, *args: Any, sender: Any = None, **kwargs: Any) -> None:
        self.emit(*args, sender=sender, **kwargs)

    def watches(self, target: str, /) -> bool:
        # IDEA: target:str|type, _qualname(target) always with watches, cons?
        return self.enabled and target in CHANNELS

    def watch[**P, R](self, func: Callable[P, R], /) -> Callable[P, R]:
        """Bind Function or Method at Startup (zero-cost no-op when disabled)"""
        if not self.watches(qual := _qualname(func)):
            return func

        is_method: bool = "." in func.__qualname__  # ty:ignore
        is_init: bool = func.__name__ in INIT  # ty:ignore

        @wraps(func)
        def _traced(*args: P.args, **kwargs: P.kwargs) -> R:
            result: R = func(*args, **kwargs)  # before _unpack!
            sender, _args = _unpack(func, qual, is_method, args)
            self.emit(f"Params: {_args=} {kwargs=}", sender=sender)
            message = (
                f"Created -> {args[0]!r}" if is_init else f"Result: {result!r}"
            )
            self.emit(message, sender=sender)
            return result

        return _traced

    @overload
    def hook_class[C](self, cls: type[C], /) -> type[C]: ...
    @overload
    def hook_class[C](
        self, /, *, methods: Sequence[str] = ()
    ) -> Callable[[type[C]], type[C]]: ...

    def hook_class[C](
        self, cls: type[C] | None = None, /, *, methods: Sequence[str] = ()
    ) -> type[C] | Callable[[type[C]], type[C]]:
        """Inject self._debug() and wrap target methods on a class."""

        # IMPORTANT: early return here? same as in watch?
        # - can cls ever change after mounting the decorator?

        def _decorator(_cls: type[C]) -> type[C]:
            active: bool = self.enabled and self.watches(_qualname(_cls))

            if not hasattr(_cls, "_debug"):
                _cls._debug = _debug if active else _noop  # ty:ignore

            if not active:
                return _cls

            for method in _dict_hits(_cls, *methods, init=self.trace_init):
                setattr(_cls, method.__name__, self.watch(method))  # ty:ignore

            return _cls

        return _decorator(cls) if cls is not None else _decorator


tap = Tap()  # TARGET: main result


#  LINE: -- Render -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _render_rich(prefix: str, *args: Any, **kwargs: Any) -> None:
    from rich import print as rprint

    rprint(f"[dim]⚡[/]{prefix}", *args, **kwargs)


def _emit(*args: Any, sender: Any = None, **kwargs: Any) -> None:
    """Active emission pipeline (only bound when CHANNELS is non-empty)."""

    # TODO: check if that is needed in every call
    # - why not bind it earlier for cls?
    if sender is not None and not isinstance(sender, str):
        if not tap.watches(_qualname(sender)):  # LATER: check earlier bind
            return

    prefix: str = f"[bold cyan]{_who(sender)}[/] [dim]│[/]" if sender else ""
    _render_rich(prefix, *args, **kwargs)

    if tap.use_loguru:
        _render_log(sender, *args)


def _render_log(sender: Any, *args: Any) -> None:
    from loguru import logger

    msg = " ".join(repr(a) if not isinstance(a, str) else a for a in args)
    logger.opt(depth=3).debug(f"[{_who(sender)}] {msg}")


#  LINE: -- Helper -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _noop(*_args: Any, **_kwargs: Any) -> None:
    """Zero-cost sink when debug is disabled."""


def _debug(self, *args, **kwargs):
    """Inject to cls"""
    tap.emit(*args, sender=self, **kwargs)


def _unpack(
    func: Callable[..., Any], qual: str, is_method: bool, args: tuple[Any, ...]
) -> tuple[str, Sequence[Any]]:
    """Resolve dynamic method sender and unbound args in one step."""
    if is_method and args:
        target, *unbound = args
        return f"{_who(target)}.{func.__name__}", unbound  # ty:ignore
    return qual, args


def _dict_hits(cls: type, *attrs: str, init: bool = False) -> list[Callable]:
    """Extract matching callables present directly in cls.__dict__."""
    methods: list = [cls.__dict__[a] for a in attrs if a in cls.__dict__]
    if init and (_init_ := _dict_hits(cls, *INIT, init=False)):
        methods.append(_init_[0])  # prefer __post_init__ if exists
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


def _qualname(target: Any, /) -> str:
    """Generate full module.qualname path for scope matching"""
    # TODO: compare with reflect.funcname|objname
    module: str = getattr(target, "__module__", "")
    qualname: str = getattr(
        target, "__qualname__", getattr(type(target), "__qualname__", "")
    )
    return f"{module}.{qualname}"  # CHECK: ".qualname"?
