"""
Loader

-
"""

__all__: list[str] = [
    "Loader",
    "Loading",
]


from collections.abc import Callable
from typing import Any, Protocol, Self

from ..empty import VOID, MayBe, MayNot


class Loading[**P, Value = Any](Protocol):  # CHECK: needed?
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Value: ...


class Loader[**P, T]:
    """Stateful lazy callable + static default resolver with selectable order."""  # NEXT:

    __slots__ = ("_fn", "_default", "_prefer_default", "_ran")  # CHECK: useful?

    @classmethod
    def from_any(  # NEXT:
        cls,
        source: MayNot[Self] | None = None,
        *,
        default: MayBe[T] = VOID,
        prefer_default: bool = False,
    ) -> Self:
        if isinstance(source, Loader):  # CHECK:
            if default is not VOID and source._default is VOID:
                source._default = default
            source._prefer_default = prefer_default
            return source
        return cls(source, default=default, prefer_default=prefer_default)

    def __init__(
        self,
        func: MayNot[Loading[P, T]] = None,
        /,
        *,
        default: MayBe[T] = VOID,
        prefer_default: bool = False,  # CHECK:
    ) -> None:
        self._fn: MayNot[Loading[P, T]] = func
        self._default: MayBe[T] = default
        # execution mode
        self._prefer_default: bool = prefer_default
        # runtime state
        self._ran: bool = False  # TODO: counter?

    def __bool__(self) -> bool:
        """True if either a callable or a static default is configured."""
        return self._fn is not None or self._default is not VOID

    @property
    def is_done(self) -> bool:
        """True if no callable is set, or the callable has already executed."""
        return self._fn is None or self._ran

    @property
    def is_pending(self) -> bool:
        """True if a callable is set and has not executed yet."""
        return self._fn is not None and not self._ran

    def bind(self, fn: Callable[P, T]) -> Callable[P, T]:
        """Attach or replace the loader callable and reset execution state."""
        self._fn: Loading[P, T] = fn
        self._ran = False
        return fn

    def reset(self) -> None:
        """Allow a one-shot loader to run again."""
        self._ran = False

    def clone(self) -> Self:
        """Create an independent copy with fresh execution state (for per-owner slots)."""
        return type(self)(
            self._fn,
            default=self._default,
            prefer_default=self._prefer_default,
        )

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        """Resolve a value using the configured order, or raise if empty."""
        if (result := self.try_resolve(*args, **kwargs)) is not VOID:
            return result
        raise LookupError(f"{self!r} has neither a callable nor a default")

    def try_resolve(self, *args: P.args, **kwargs: P.kwargs) -> MayBe[T]:
        """Resolve a value according to prefer_default, returning VOID if empty."""
        if self._prefer_default:
            if self._default is not VOID:
                return self._default
            if self._fn is not None:
                self._ran = True
                return self._fn(*args, **kwargs)
        else:
            if self._fn is not None:
                self._ran = True
                return self._fn(*args, **kwargs)
            if self._default is not VOID:
                return self._default
        return VOID

    def once(self, *args: P.args, **kwargs: P.kwargs) -> MayBe[T]:
        """Execute at most once; returns VOID if already ran or unconfigured."""
        if self._ran:
            return VOID
        result: MayBe[T] = self.try_resolve(*args, **kwargs)
        self._ran = True
        return result

    def __repr__(self) -> str:  # TASK: show Name[T], figure out T
        fn_name: str = getattr(self._fn, "__name__", repr(self._fn))
        return (
            f"Loader(fn={fn_name}, default={self._default!r}, "
            f"ran={self._ran}, prefer_default={self._prefer_default})"
        )
