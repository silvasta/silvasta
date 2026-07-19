import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import ParamSpec, TypeVar

from loguru import logger

P = ParamSpec("P")
R = TypeVar("R")


@dataclass(frozen=True)
class BaseFunctor(Generic[P, R]):
    """Generic Callable Object Base"""

    name: str
    func: Callable[P, R]

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.func(*args, **kwargs)

    def execute_safely(
        self, *args: P.args, exit_code: int = 1, **kwargs: P.kwargs
    ) -> R | None:
        try:
            return self(*args, **kwargs)
        except Exception as error:
            logger.critical(f"{self} failed: {error}")
            sys.exit(exit_code)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.name}]"
