import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass(frozen=True)
class Functor:
    """Functor: Handle..."""

    name: str
    func: Callable[[Any], Any]

    def __call__(self, *args, **kwargs) -> Any:
        """Execute handler function"""
        self.func(*args, **kwargs)

    def protected(self, *args, **kwargs) -> Any:
        """Execute handler function and terminate safely"""
        try:
            self(*args, **kwargs)
        except Exception as error:
            logger.critical(f"{self} failed: {error}")
            sys.exit(1)

    # ...plus other views
    def __str__(self) -> str:
        return f"{type(self).__name__}[ImportantAttribute]"
