import sys
from collections.abc import Callable
from dataclasses import dataclass

from loguru import logger


@dataclass(frozen=True)
class ErrorHandler[E: BaseException]:
    """Functor to safely execute CLI exception formatting and termination."""

    name: str  # LATER: think about how to generalize
    exception_type: type[E]  # MOVE: property? cached_property? __post_init__?
    func: Callable[[E], None]
    exit_code: int = 1

    def __str__(self) -> str:
        return f"ErrorHandler[{self.exception_type.__name__}]"

    # LATER: think about how and if using: __call__

    def execute_safe(self, error: E) -> None:
        """Executes the handler, then terminates the CLI safely."""
        try:
            self.func(error)
            sys.exit(self.exit_code)  # Centralized exit!

        except SystemExit:
            raise  # Respect if the raw function explicitly calls sys.exit()

        except Exception as handler_fail:
            logger.critical(f"{self} failed during formatting: {handler_fail}")
            logger.error(f"Initial Error was: {error}")
            sys.exit(2)
