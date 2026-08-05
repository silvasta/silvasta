"""
Provide Schema with defaults

- SstModel: Slighly modified BaseModel with frequently used functions
                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "SstModel",
]

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Self

from loguru import logger
from pydantic import BaseModel, Field

# TASK: rework
# - check with latest projects
# - attach (optional) views


class SstModel(BaseModel):
    """Extend Defaults of Pydantic BaseModel"""

    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def build_from_file(cls, path: Path) -> Self:
        """Load saved state from json and build Model"""
        return cls.model_validate(
            json.loads(path.read_text(encoding="utf-8")),
        )

    def touch(self):
        """Update internal parameter after change"""
        self.last_updated: datetime = datetime.now(UTC)
        logger.debug(f"state file: {self.last_updated=}")

    def save_to_file(self, path: Path):
        """Save current state to json after final update"""
        self.touch()
        path.write_text(self.json_content(), encoding="utf-8")

    def json_content(self) -> str:
        """Dump with defaults"""
        return self.model_dump_json(exclude_defaults=False, indent=2)
