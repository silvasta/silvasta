import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from loguru import logger

from sstcore.contract.event import EmitFunc, Event, EventName

# P = ParamSpec("P")
# R = TypeVar("R")


class ErrorPolicy(StrEnum):
    LOG_AND_CONTINUE = "log"
    LOG_AND_EXIT = "exit"
    RE_RAISE = "raise"


# Core reusable pieces
class NamedMixin:
    name: str
    tags: set[str] = field(default_factory=set)

    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.name}]"

    def __repr__(self) -> str:
        return f"{self}({self.tags or ''})"


class SafeExecutionMixin[P, R]:
    """Cross-cutting resilience."""

    error_policy: ErrorPolicy = ErrorPolicy.LOG_AND_CONTINUE
    exit_code: int = 1

    def safe_call(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return self.__call__(*args, **kwargs)  # type: ignore
        except Exception as exc:
            return self._handle_error(exc, *args, **kwargs)

    def _handle_error(self, exc: Exception, *args, **kwargs) -> R | None:
        logger.critical(f"{self} failed: {exc}")
        if self.error_policy == ErrorPolicy.LOG_AND_EXIT:
            logger.error(f"Original error: {exc}")
            sys.exit(self.exit_code)
        elif self.error_policy == ErrorPolicy.RE_RAISE:
            raise
        return None


class FactoryMixin:
    """Common introspection factories."""

    @classmethod
    def from_callable(
        cls,
        func: Callable[P, R],
        name: str | None = None,
        **metadata: Any,
    ):
        name = name or getattr(func, "__name__", "unnamed")
        # Subclasses can add signature inference here (like your ErrorHandler.from_func)
        return cls(name=name, func=func, **metadata)  # type: ignore


# Concrete base for simple cases
@dataclass(frozen=True)
class Functor[P, R](NamedMixin, SafeExecutionMixin[P, R], FactoryMixin):
    """Lightweight default for most handlers."""

    func: Callable[P, R]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.func(*args, **kwargs)


# Specialized versions (inherit only what they need)
@dataclass(frozen=True)
class EventHandler(Functor[[Event], None]):
    fail_loud: bool = False

    def __call__(self, event: Event) -> None:
        try:
            self.func(event)
        except Exception as e:
            if self.fail_loud:
                raise RuntimeError(f"Critical fail in {self}") from e
            logger.error(f"{self} failed for '{event.name}': {e}")


@dataclass(frozen=True)
class ErrorHandler[Error: BaseException](Functor[[Error], None]):
    exception_type: type[Error]
    exit_code: int = 1

    # Keep your excellent from_func + signature inference
    ...


@dataclass(frozen=True)
class EmitFunctor(NamedMixin, FactoryMixin):
    """Stays close to current elegant design (partial-like)."""

    emit: EmitFunc
    event_name: EventName
    sender: str
    defaults: dict[str, Any] = field(default_factory=dict)

    def __call__(self, **overrides: Any) -> None:
        payload = {**self.defaults, **overrides}
        self.emit(self.event_name, self.sender, **payload)
