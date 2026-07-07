# TODO: explain

import json
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Self

from loguru import logger
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

from sstcore.utils.time import nice_duration

from ..utils.log import LogParam
from .defaults import SstDefaults
from .names import SstNames


class SstSettings(BaseSettings):
    """Container for Defaults and Names and Frame for setting file"""

    names: SstNames = Field(default_factory=SstNames)
    defaults: SstDefaults = Field(default_factory=SstDefaults)
    log: LogParam = Field(default_factory=LogParam)

    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updates: deque[datetime] = Field(default_factory=deque)
    update_maxlen: int = 79

    @classmethod
    def load(cls, path: Path) -> Self:
        """Load current status from json"""
        return cls.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def save(self, path: Path):
        """Refresh datetime and save current status to json"""
        before: datetime = self.last_updated
        self.touch()
        duration: str = nice_duration(before, after=self.last_updated)
        logger.info(f"Settings updated after {duration}")
        path.write_text(self.json_content(), encoding="utf-8")

    @classmethod
    def default_json_content(cls) -> str:
        """Get unmodified json content of all class members"""
        return cls().model_dump_json(
            exclude_defaults=False,
            indent=2,
        )

    def json_content(self, exclude_defaults=False) -> str:
        """Dump content of all class members with custom indent"""
        return self.model_dump_json(
            exclude_defaults=exclude_defaults,
            indent=2,
        )

    def touch(self):
        """Update datetime and check maxlen of saved updates"""
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
