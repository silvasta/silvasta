import json
from datetime import datetime, timedelta
from typing import Generic, TypeVar, cast

from loguru import logger

from .settings import BaseDefaults, BaseNames, BasePaths, Settings

# Define specific TypeVars for everything
TSettings = TypeVar("TSettings", bound=Settings)
TNames = TypeVar("TNames", bound=BaseNames)
TDefaults = TypeVar("TDefaults", bound=BaseDefaults)
TPaths = TypeVar("TPaths", bound=BasePaths)


class ConfigManager(Generic[TSettings, TNames, TDefaults, TPaths]):
    """Provide singleton with all settings and factories"""

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
        self.paths: TPaths = self._paths_cls(names=self.settings.names)

        if self._user_file.exists() and self._load_user_prefs():
            # logger.info("Settings loaded from file")
            # Rebuild to get the new reference (in case of changes)
            self.paths: TPaths = self._paths_cls(names=self.settings.names)
        else:
            logger.info("Using default settings created from scratch")
            if save_defaults_to_file:
                self.save()

    @property
    def _user_file(self):
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
    def starttime(self) -> str:
        return self._starttime.strftime(self.names.timestamp_format)

    @property
    def duration(self) -> timedelta:  # NOTE: how and where to apply a format?
        return datetime.now() - self._starttime

    def _load_user_prefs(self) -> bool:
        try:
            data = json.loads(self._user_file.read_text(encoding="utf-8"))
            self.settings: TSettings = self._settings_cls.model_validate(data)
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
