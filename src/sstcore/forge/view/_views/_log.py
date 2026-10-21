"""
Compose LogMixins

- Atomize: 1 class with 1 method __log__

                             DependencyLevel.sstcore.brick.views[0]
"""

__all__: list[str] = [
    "LogDataMixin",
    "FullLogMixin",
]

from typing import Any

from ....brick.reflect import scan
from ....port.event.dto import LogDTO


class LogDataMixin:
    """Show public attributes"""

    def __log__(self) -> LogDTO:
        return LogDTO(
            message=str(self),
            level="INFO",
            metrics=scan.pydantic(self),
        )


class FullLogMixin:
    """Show specific class attributes defined in _panel_data"""

    @property
    def _log_metrics(self) -> dict[str, Any]:
        return vars(self)

    def __log__(self) -> LogDTO:
        return LogDTO(
            message=f"{self}",
            level="INFO",
            metrics=self._log_metrics,
        )
