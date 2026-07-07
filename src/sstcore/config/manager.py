"""
Orchestrate Config and Settings

- Launch bootstrap and home setup
- Load and save Settings from file
- Provide access to Defaults, Names and Paths

"""

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

from dotenv import load_dotenv
from loguru import logger

from ..utils import HomeSetup, Printer, day_count
from .bootstrap import BootDefaults, BootResult, ConfigBootstrap
from .defaults import SstDefaults
from .names import SstNames
from .paths import SstPaths
from .settings import SstSettings


class ConfigManager[
    TSettings: SstSettings,
    TNames: SstNames,
    TDefaults: SstDefaults,
    TPaths: SstPaths,
]:
    """Bundle Container and Factories and provide access as Singleton"""

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
        self.settings: TSettings = settings_cls.load(self.setting_file)
        self.paths: TPaths = paths_cls(self.names, self.defaults, home_setup)

        self._fill_printer()  # important to get title in Panel
        self._env_loaded = False

    def save_settings(self):
        """Provide access to save Setting file"""
        self.settings.save(self.setting_file)
        logger.info(f"Settings saved to: {self.setting_file}")

    def __str__(self) -> str:
        return type(self).__name__

    # NEXT: proper __fmt__

    def __repr__(self) -> str:
        settings: str = type(self.settings).__name__
        paths: str = type(self.settings).__name__
        defaults: str = type(self.defaults).__name__
        names: str = type(self.names).__name__
        return f"{self}[{settings}, {paths}, {defaults},{names}]"

    def _fill_printer(self):
        Printer.project_name = self.project_name
        Printer.project_version = self.project_version

    @property
    def names(self) -> TNames:
        """Provide Names instance access with enforced dot access"""
        return cast(TNames, self.settings.names)

    @property
    def defaults(self) -> TDefaults:
        """Provide Defaults instance access with enforced dot access"""
        return cast(TDefaults, self.settings.defaults)

    @property
    def dom(self) -> int:
        return day_count()

    @property
    def starttime(self) -> str:
        return self._starttime.strftime(self.defaults.timestamp_format)

    @property
    def duration(self) -> timedelta:
        return datetime.now(UTC) - self._starttime

    @property
    def timestamp(self) -> str:
        return datetime.now(UTC).strftime(self.defaults.timestamp_format)

    def from_env(self, key: str):
        """Ensure .env is loaded, get env var with key or raise Error"""

        if not self._env_loaded:
            load_dotenv(self.paths.dot_env())
            self._env_loaded = True

        if (var := os.getenv(key)) is not None:
            return var

        raise ValueError(f"Missing {key=} in os.env despite loaded .env")
