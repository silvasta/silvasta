import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field, field_validator

from ..utils import HomeSetup, Printer, day_count
from ..utils.log import LogParam
from .bootstrap import BootDefaults, BootResult, ConfigBootstrap
from .defaults import SstDefaults
from .names import SstNames
from .paths import SstPaths
from .settings import SstSettings

type ConfigTypes = SstDefaults | SstNames | SstPaths | SstSettings


class ConfigManager[
    TSettings: SstSettings,
    TNames: SstNames,
    TDefaults: SstDefaults,
    TPaths: SstPaths,
]:
    """Provide singleton with all settings and factories"""

    _env_loaded = False

    @property
    def names(self) -> TNames:
        """Explicit return of Generic type with dot access"""
        return cast(TNames, self.settings.names)

    @property
    def defaults(self) -> TDefaults:
        """Explicit return of Generic type with dot access"""
        return cast(TDefaults, self.settings.defaults)

    def __init__(
        self,
        settings_cls: type[TSettings],
        paths_cls: type[TPaths],
        setting_file: Path | None = None,
        project_name: str = "",
        project_root: Path | None = None,
        home_setup: HomeSetup = HomeSetup.PROJECT,
    ):
        self._starttime: datetime = datetime.now(UTC)

        boot: BootResult = ConfigBootstrap.initial_setup(
            settings_cls,
            defaults=BootDefaults(
                project_name=project_name,
                project_root=project_root,
                home_setup=home_setup,
                setting_file=setting_file,
            ),
        )
        self.project_name: str = boot.project_name
        self.project_version: str = boot.project_version

        self.setting_file: Path = boot.setting_file
        self.settings: TSettings = self._load_settings(settings_cls)
        self.paths: TPaths = self._load_paths(paths_cls, home_setup)

        self._fill_printer()  # important to get title in Panel

    def save_settings(self):
        self.settings.save(self.setting_file)
        logger.info(f"Settings saved to: {self.setting_file}")

    def _load_settings(self, settings_cls: type[TSettings]) -> TSettings:
        settings: TSettings = settings_cls.load(self.setting_file)
        logger.debug(f"{self.name} loaded: {settings_cls.__name__}")
        return settings

    def _load_paths(
        self, paths_cls: type[TPaths], home_setup: HomeSetup
    ) -> TPaths:
        paths: TPaths = paths_cls(
            names=self.names, defaults=self.defaults, homes=home_setup
        )
        logger.debug(f"{self.name} loaded: {paths_cls.__name__}")
        return paths

    def _fill_printer(self):
        Printer.project_name = self.project_name
        Printer.project_version = self.project_version

    @property
    def home_setup(self) -> HomeSetup:
        return self.paths._homes

    @property
    def log_path(self) -> Path:
        return self.settings.log.log_file

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def dom(self) -> int:
        return day_count()

    @property
    def starttime(self) -> str:
        return self._starttime.strftime(self.defaults.timestamp_format)

    @property
    def duration(self) -> timedelta:  # LATER: where and how to apply format?
        return datetime.now(UTC) - self._starttime

    @property
    def timestamp(self) -> str:
        return datetime.now(UTC).strftime(self.defaults.timestamp_format)

    def from_env(self, key: str):
        """get variable from environment, log failure, raise error"""
        if not self._env_loaded:
            load_dotenv(self.paths.dot_env)
            self._env_loaded = True
        var: str = os.getenv(key, "fail")  # NOTE: stable enough?
        if var == "fail":
            logger.error(f"failed to load env var with {key=}")
            raise ValueError("Value not found in os.env or with loaded .env")
        return var

    @property
    def setup_info(self) -> ConfigSetupParam:
        return ConfigSetupParam(
            config_file=self.setting_file,
            project_name=self.project_name,
            project_version=self.project_version,
            log=self.settings.log.with_source("Custom: config.settings.log"),
        )


class ConfigSetupParam(BaseModel):
    """Used to hand-over trough CLI setup pipeline, app.main -> callback -> setup logging"""

    config_file: Path
    project_name: str = ""
    project_version: str = ""
    log: LogParam = Field(default_factory=LogParam)

    @field_validator("config_file")
    @classmethod
    def ensure_path(cls, v: Path | str):
        return Path(v)
