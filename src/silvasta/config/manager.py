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
        # LATER: load setting independent of paths
        # IDEA: load paths with settings?
        # - Paths gets anyway names and defaults!
        self.paths: TPaths = self._load_paths()

        if self._load_user_prefs_from_file():
            # Rebuild paths in case of changes
            self.paths: TPaths = self._load_paths()
            logger.info("Settings loaded from file")
        else:
            if save_defaults_to_file:
                self.save()
            logger.info("Using default settings created from scratch")

    @property
    def _user_file(self):
        # REMOVE: separate paths/user_setting_file
        return self.paths.user_setting_file

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
        return self._starttime.strftime(self.names.timestamp_format)

    @property
    def duration(self) -> timedelta:
        # LATER: how and where to apply a format?
        return datetime.now() - self._starttime

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

    def _load_user_prefs_from_file(self) -> bool:
        if not self._user_file.exists():
            logger.info("No user_setting_file found")
            return False
        try:
            data = json.loads(self._user_file.read_text(encoding="utf-8"))
            self.settings: TSettings = self._settings_cls.model_validate(data)
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
        self._user_file.write_text(json_str, encoding="utf-8")
        logger.info(f"Settings saved to: {self._user_file}")
