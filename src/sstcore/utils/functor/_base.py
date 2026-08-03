import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Self

from loguru import logger

from ...port.functor import ErrorPolicy


class NamedMixin:
    name: str
    tags: set[str] = field(default_factory=set)

    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.name}]"

    def __repr__(self) -> str:
        return f"{self}({self.tags or ''})"


class FactoryMixin[**P, R]:
    """Common introspection factories."""

    @classmethod
    def from_func(
        cls,
        func: Callable[P, R],
        name: str | None = None,
        **metadata: Any,
    ) -> Self:
        name: str = name or getattr(func, "__name__", "unnamed")
        # Subclasses can add signature inference here
        return cls(name=name, func=func, **metadata)


class SafeExecutionMixin[**P, R]:
    """Cross-cutting resilience."""

    error_policy: ErrorPolicy = ErrorPolicy.LOG_AND_CONTINUE
    exit_code: int = 1

    def safe_call(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return self(*args, **kwargs)
        except Exception as error:
            return self._handle_error(error, *args, **kwargs)

    def _handle_error(self, error: Exception, *args, **kwargs) -> R | None:
        logger.critical(f"{self} failed: {error}")

        match self.error_policy:
            case ErrorPolicy.LOG_AND_CONTINUE:
                return None

            case ErrorPolicy.LOG_AND_EXIT:
                logger.error(f"Original error: {error}")
                sys.exit(self.exit_code)

            case ErrorPolicy.RE_RAISE:
                raise


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Assembly
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@dataclass(frozen=True, kw_only=True)
class Functor[**P, R](
    NamedMixin, SafeExecutionMixin[P, R], FactoryMixin[P, R]
):
    """Lightweight default for most handlers."""

    func: Callable[P, R]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.func(*args, **kwargs)
