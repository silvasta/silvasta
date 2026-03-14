import json

from loguru import logger

from .settings import BaseDefaults, BaseNames, BasePaths, Settings

from typing import Generic, TypeVar

T = TypeVar("T", bound=Settings)


class ConfigManager(Generic[T]):
    """Provide singleton with all settings and factories"""

    def __init__(self, settings: T, save_defaults_to_file=True):
        self.settings = Settings()

        if self._user_file.exists() and self._load_user_prefs():
            logger.info("Settings loaded from file")
        else:
            logger.info("Using default settings created from scratch")
            if save_defaults_to_file:
                self.save()

    @property
    def _user_file(self):
        return self.paths.user_setting_file

    @property
    def names(self) -> BaseNames:
        return self.settings.names

    @property
    def paths(self) -> BasePaths:
        return self.settings.paths

    @property
    def defaults(self) -> BaseDefaults:
        return self.settings.defaults

    def _load_user_prefs(self) -> bool:
        try:
            data = json.loads(self._user_file.read_text(encoding="utf-8"))
            self.settings: Settings = Settings.model_validate(data)
            return True
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return False

    def save(self):
        json_str: str = self.settings.model_dump_json(
            exclude_defaults=False,
            indent=2,
        )
        self._user_file.write_text(json_str, encoding="utf-8")
        logger.info(f"Settings saved to: {self._user_file}")
