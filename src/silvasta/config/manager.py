import json
import os
from datetime import datetime, timedelta
from typing import Generic, cast

from dotenv import load_dotenv
from loguru import logger

from silvasta.utils import day_count

from .paths import TPaths
from .settings import TDefaults, TNames, TSettings


class ConfigManager(Generic[TSettings, TNames, TDefaults, TPaths]):
    """Provide singleton with all settings and factories"""

    _env_loaded = False

    def __init__(
        self,
        settings_cls: type[TSettings],
        paths_cls: type[TPaths],
        save_defaults_to_file: bool = True,
    ):
        self._starttime: datetime = datetime.now()

        self._settings_cls: type[TSettings] = settings_cls
        self._paths_cls: type[TPaths] = paths_cls

        self.settings: TSettings = self._settings_cls()
        self.paths: TPaths = self._load_paths()

        if not self._load_settings_from_file():
            logger.info("Using default settings created from scratch")
            if save_defaults_to_file:
                self.save()
        else:
            logger.info("Settings loaded from file")

    @property
    def names(self) -> TNames:
        """Explicit return of Generic type with dot access"""
        return cast(TNames, self.settings.names)

    @property
    def defaults(self) -> TDefaults:
        """Explicit return of Generic type with dot access"""
        return cast(TDefaults, self.settings.defaults)

    @property
    def dom(self) -> int:
        return day_count()

    @property
    def starttime(self) -> str:
        return self._starttime.strftime(self.defaults.timestamp_format)

    @property
    def duration(self) -> timedelta:
        # LATER: how and where to apply a format?
        return datetime.now() - self._starttime

    @property
    def timestamp(self) -> str:
        return datetime.now().strftime(self.defaults.timestamp_format)

    def from_env(self, key: str):
        """get variable from environment, log failure, raise error"""
        if not self._env_loaded:
            load_dotenv(self.paths.dot_env)
            self._env_loaded = True
        var: str = os.getenv(key, "fail")
        if var == "fail":
            logger.error(f"failed to load credentials! ({key})")
            raise ValueError("Login credentials not found in .env file")
        return var

    def _load_settings_from_file(self) -> bool:

        if not (setting_file := self.paths.setting_file).exists():
            logger.info(f"Nothing found at: {setting_file=}")
            return False
        try:
            self.settings: TSettings = self._settings_cls.model_validate(
                json.loads(setting_file.read_text(encoding="utf-8"))
            )
            self.paths: TPaths = self._load_paths()  # Reload for changes
            return True

        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return False

    def _load_paths(self) -> TPaths:
        return self._paths_cls(
            names=self.settings.names, defaults=self.settings.defaults
        )

    def save(self):
        json_str: str = self.settings.model_dump_json(
            exclude_defaults=False,
            indent=2,
        )
        self.paths.setting_file.write_text(json_str, encoding="utf-8")
        logger.info(f"Settings saved to: {self.paths.setting_file}")
