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
from ._define import Channels, PortEmit, Redacting
from ._functional import INIT, _dict_hits, _qual, _unpack, _who

HAND_TOGGLE: tuple[str, ...] = (
    "color",
    "vault",
    "init",
)


# MOVE: as Tap.channels?
CHANNELS = Channels(env_var="SST_DEBUG", default=HAND_TOGGLE)


class Tap:
    """Minimal debug probe for port, brick, and forge bring-up."""

    __slots__ = ("channels", "enabled", "trace_init", "use_loguru", "emit")

    def __init__(
        self, env_var: str = "SST_DEBUG", toggle: Iterable[str] = HAND_TOGGLE
    ):
        """Bind once at startup: zero branching overhead when OFF"""
        self.configure(env_var=env_var, toggle=toggle)
        self.emit: PortEmit = _emit if self.enabled else _noop

    def configure(
        self, env_var: str = "SST_DEBUG", toggle: Iterable[str] = ()
    ) -> Self:
        """Mutate Tap state in-place so all downstream imports see the new rules."""

        self.channels = Channels(env_var=env_var, default=tuple(toggle))
        self.trace_init: bool = self.channels.has("init")
        self.use_loguru: bool = self.channels.has("log")
        self.emit: PortEmit = _emit if self.enabled else _noop

        return self

    def __bool__(self) -> bool:
        return bool(self.channels)

    def __call__(self, *args: Any, sender: Any = None, **kwargs: Any) -> None:
        self.emit(*args, sender=sender, **kwargs)

    def watches(self, target: str, /) -> bool:
        # IDEA: target:str|type, _qual(target) always with watches, cons?
        # NEXT: even better, directly use Channels for that!
        # - why only accept str there? place render rule there!
        return self.enabled and target in CHANNELS

    def watch[**P, R](self, func: Callable[P, R], /) -> Callable[P, R]:
        """Bind Function or Method at Startup (zero-cost no-op when disabled)"""
        if not self.watches(qual := _qual(func)):
            return func

        # MOVE: _functional?
        is_method: bool = "." in func.__qualname__  # ty:ignore
        # MOVE: _functional?
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
    def trace[C](self, cls: type[C], /) -> type[C]: ...
    @overload
    def trace[C](
        self, /, *, methods: Sequence[str] = ()
    ) -> Callable[[type[C]], type[C]]: ...

    def trace[C](
        self, cls: type[C] | None = None, /, *, methods: Sequence[str] = ()
    ) -> type[C] | Callable[[type[C]], type[C]]:
        """Inject self._debug() and wrap target methods on a class."""

        # NEXT: replace "if cls is not None" in the last line of this fn
        # if not tap.watches(_qual(cls)):  # FIX: is this even needed?
        #     return cls  # FIX: maybe move active=... out of decorator? know before?

        def _decorator(_cls: type[C]) -> type[C]:
            active: bool = self.enabled and self.watches(_qual(_cls))

            if not hasattr(_cls, "_debug"):
                # NOTE: Projector primitive?
                _cls._debug = _debug if active else _noop  # ty:ignore

            if not active:
                return _cls

            for method in _dict_hits(_cls, *methods, init=self.trace_init):
                # NOTE: Projector primitive?
                setattr(_cls, method.__name__, self.watch(method))  # ty:ignore

            return _cls

        return _decorator(cls) if cls is not None else _decorator


#  LINE: -- Directly used by Tap -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _noop(*_: Any, **__: Any) -> None:
    """Zero-cost sink when debug is disabled."""


tap: Any = None  # REMOVE:


def _debug(self, *args, **kwargs):
    """Inject this to cls"""
    tap.emit(*args, sender=self, **kwargs)  # FIX:


def _emit(*args: Any, sender: Any = None, **kwargs: Any) -> None:
    """Active emission pipeline (only bound when CHANNELS is non-empty)."""

    sender: str = _who(sender)

    _render._rich(sender, *args, **kwargs)

    if tap.use_loguru:  # FIX:
        _render._loguru(sender, *args)


#  LINE: -- The final Config?? -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LinkConfig(Protocol):  # MOVE: to _define when finished
    """The Part intended for separated mutable dataclass"""

    @property
    def emit(self) -> PortEmit: ...
    def ignores(self, base: type) -> bool: ...


@dataclass(frozen=True, slots=True)
class LinkSpec:
    emit: PortEmit
    merge: Redacting
    #
    skip: frozenset[type] = frozenset({object, Protocol, Generic})
    # TODO: error strategy? or maybe this is fixed

    def ignores(self, base: type) -> bool:
        return base in self.skip

    def derive(self, **kwargs) -> Self:
        # TODO: when setup clear:
        # **kwargs:Unpack[LinkInput] or similar, or just hardcode forward param
        return replace(self, **kwargs)

    def surface(self, protocol: type) -> list[str]:
        """Generate target Protocol Attrs using '' for the Cls itself"""
        cls_as_attribute: list[str] = [""]
        return cls_as_attribute + list(get_protocol_members(protocol))

    def configure(self, **kwargs: Any) -> Self:
        """Mutate this LinkSpec in-place for global project-wide changes."""
        for k, v in kwargs.items():
            if not hasattr(self, k):
                raise AttributeError(f"Unknown LinkSpec option: {k!r}")
            setattr(self, k, v)
        return self


if TYPE_CHECKING:
    _: type[LinkConfig] = LinkSpec
