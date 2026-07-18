"""
Compose LogMixins

- Atomize: 1 class with 1 method __log__
"""

from typing import Any

from pydantic import BaseModel

from ....contract.log import LogDTO


class DebugLogMixin:
    def __log__(self) -> LogDTO:
        data: dict[str, Any] = vars(self)
        return LogDTO(message=str(self), level="INFO", metrics=data)


class PydanticDataMixin:  # TODO: some (protocol) check with Pydantic
    def __log__(self) -> LogDTO:
        if not isinstance(self, BaseModel):
            return LogDTO(f"{self}: Bad Mixin!", level="ERROR")
        data: dict[str, Any] = self.model_dump()
        return LogDTO(message=str(self), level="INFO", metrics=data)


class LogMixin:
    def __log__(self) -> LogDTO:
        name: str = type(self).__name__
        metrics: dict[str, Any] = {  # COLLECT: consider all the pattern
            k: v for k, v in vars(self).items() if not k.startswith("_")
        }
        return LogDTO(message=f"{name}", level="INFO", metrics=metrics)
