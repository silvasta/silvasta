"""
Parse Names and Extract Keys - supported with validated BaseModel access

Example with LogMeta below (dataclass with: level:str ,date:str
# IDE knows exactly that `parser.extract` returns a `LogMeta` instance
parser: ParsedName[LogMeta] = ParsedName("{level}_{date}.log", factory=LogMeta)

backwards = parser("ERROR_2026-07-31.log")  # ty shows LogMeta as type

forward = LogMeta("INFO", "26-07-31")
log_string = parser(forward)
                                                       DependencyLevel[2]
"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast, overload

from ._core import NameParser

__all__: list[str] = [
    "ParsedName",
]


@dataclass
class LogMeta:  # NOTE: Example
    level: str
    date: str


class ParsedName[DTO](NameParser):
    """
    Switch bidirectional between Keywords and String

    - Without factory DTO resolves to dict[str, Any]

    """

    def __init__(
        self,
        pattern: str,
        factory: Callable[..., DTO] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(pattern=pattern, **kwargs)
        self.factory: Callable[..., DTO] | None = factory

    @overload
    def __call__(self, target: Path | str) -> DTO: ...

    @overload
    def __call__(self, target: DTO) -> str: ...

    @overload
    def __call__(self, target: dict | list | tuple) -> str: ...

    def __call__(self, target: Any) -> Any:
        """Route Target to Extract (String -> DTO) or Format (DTO -> String)"""

        if isinstance(target, (Path, str)):
            raw: dict[str, Any] = super().__call__(target)

            if self.factory is None:
                return cast(DTO, raw)

            return self.factory(**raw)

        if isinstance(target, (dict, list, tuple)):
            return super().__call__(target)

        if hasattr(target, "_asdict"):
            # NamedTuple support
            target: dict[str, Any] = target._asdict()
        elif hasattr(target, "__dict__"):
            # Dataclass & Standard Class support
            target: dict[str, Any] = vars(target)
        elif hasattr(target, "model_dump"):
            # Graceful fallback if Pydantic sneaks in
            target: dict[str, Any] = target.model_dump()

        return super().__call__(target)
