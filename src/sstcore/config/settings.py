from datetime import UTC, datetime
from pathlib import Path

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings

from ..utils import PathGuard
from ..utils.path import XdgHomes
from .defaults import SstDefaults
from .names import SstNames


class SstSettings(BaseSettings):
    """Default settings and names, written to and loaded from file"""

    names: SstNames = Field(default_factory=SstNames)
    defaults: SstDefaults = Field(default_factory=SstDefaults)
    last_updated: datetime = datetime.now(UTC)

    @classmethod
    def default_json_content(cls) -> str:
        """Get unmodified dumped content of all class members"""
        return cls().model_dump_json(
            exclude_defaults=False,
            indent=2,
        )

    @classmethod
    def ensure_master_setting_file(
        cls, write_new_file_if_missing: bool
    ) -> Path:
        """If file not exists, {write default content and} get Error"""

        master_file_path: Path = cls._master_file_path()
        content: str | None = (
            cls.default_json_content() if write_new_file_if_missing else None
        )
        try:
            PathGuard.file(
                target=master_file_path,
                default_content=content,
                raise_error=True,
            )
            logger.debug("master_setting_file ensured")
            return master_file_path

        except FileNotFoundError:
            if not write_new_file_if_missing:
                raise FileNotFoundError(
                    "Place master_setting_file at location or write default!"
                ) from None  # TEST: how does the error look in cli?

        logger.info("New master_setting_file written from default Settings")
        return (
            cls.ensure_master_setting_file(  # Again to check if write worked
                write_new_file_if_missing=False,  # False to avoid loop
            )
        )

    @classmethod
    def _master_file_path(cls) -> Path:
        """Generate immutable path to load Settings or finding setting_file!"""
        # IDEA: _master_file_path : Path|None = None
        # if _master_file_path:
        #   return _master_file_path
        tmp_names: SstNames = cls().names  # HACK: somehow strange
        return (
            XdgHomes("config").path
            / tmp_names.project
            / tmp_names.setting_file
        )

    def save_to_path(self, path: Path):
        """Save current status to json"""
        self.last_updated: datetime = datetime.now(UTC)
        path.write_text(self.json_content(), encoding="utf-8")

    def save_to_master_setting_file(self):
        self.save_to_path(self._master_file_path())
        logger.debug("saved to master_file_path")

    def json_content(self) -> str:
        """Dump content of all class members"""
        return self.model_dump_json(
            exclude_defaults=False,
            indent=2,
        )
