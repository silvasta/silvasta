"""
Provide Interface for serializable Components

- Synchronize Defaults, Names and LogParam from and to disk
- Ensure reliable and observable setting file handling
                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "SstSettings",
]

import json
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Self

from loguru import logger
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

from ...brick.time import nice_duration
from ...port.config import Settings
from ...port.link import portlink
from ...util.log import LogParam
from ._defaults import SstDefaults
from ._names import SstNames


@portlink(Settings)
class SstSettings(BaseSettings):
    """Hold the last loaded file path (useless for boot)"""

    file: Path
    defaults: SstDefaults = Field(default_factory=SstDefaults)
    names: SstNames = Field(default_factory=SstNames)
    log: LogParam = Field(default_factory=LogParam)  # WARN: defaults not seen?

    last_updated: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updates: deque[datetime] = Field(default_factory=deque)
    update_maxlen: int = 80

    @classmethod
    def load(cls, file: Path) -> Self:
        _data = json.loads(file.read_text(encoding="utf-8"))
        settings: Self = cls.model_validate(_data)
        if file != settings.file:
            logger.info(f"Changing {settings.file=} to {file=}")
            settings.file = file  # CHECK: here or in .save??
            settings.save(settings.file)
        return settings

    def save(
        self,
        file: Path,  # CHECK: still required as non-optional?
    ) -> None:
        self.file: Path = file
        before: datetime = self.last_updated
        self.touch()
        duration: str = nice_duration(start=before, end=self.last_updated)
        logger.info(f"Settings updated after {duration}")
        file.write_text(self.json_content(), encoding="utf-8")

    @classmethod
    def default_json_content(cls) -> str:
        # LATER: just json and with some dispatch?
        """Get unmodified json content with all class members"""
        return cls().json_content(exclude_defaults=False)

    def json_content(self, exclude_defaults=False) -> str:
        # LATER: just json?
        """Dump content of all class members with custom indent"""
        return self.model_dump_json(
            exclude_defaults=exclude_defaults,
            indent=2,
        )

    def touch(self) -> None:
        n_saved_update_times: int = self.update_maxlen
        if n_saved_update_times != (before := self.updates.maxlen):
            self.updates: deque[datetime] = deque(
                self.updates, maxlen=n_saved_update_times
            )
            logger.success(f"Changed: {n_saved_update_times=} ({before=})")
        self.updates.append(update := datetime.now(UTC))
        self.last_updated: datetime = update

    @model_validator(mode="after")
    def enforce_deque_maxlen(self) -> Self:
        desired_maxlen: int = self.update_maxlen
        if self.updates.maxlen != desired_maxlen:
            self.updates: deque[datetime] = deque(
                iterable=self.updates,
                maxlen=desired_maxlen,
            )
        return self
