"""
Orchestrate Config and Settings

- Launch bootstrap, home setup and govern results
- Load and save Settings from and to file
- Provide access to Defaults, Names and Paths

Usage in Projects:
  - Create custom components (mainly fill Defaults, Names and Paths)
  - Launch with config_loader, collect instance if desired
  - Access by instance or global singleton, forget about this setup

                                                       DependencyLevel[2]
"""

__all__: list[str] = [
    "ConfigManager",
]

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Self

from dotenv import load_dotenv
from loguru import logger

from ...brick.format import cls_name
from ...brick.time import day_count
from ...port.config import Config, Defaults, Homes, Log, Names, Paths, Settings
from ...util.log import setup_logging
from ._homes import HomeSetup, ProjectInfo, SstHomes
from ._paths import SstPaths
from ._settings import SstSettings


class ConfigManager:
    """Bundle Container and Factories and provide access as Singleton"""

    def __init__(self, settings: Settings, paths: Paths, info: ProjectInfo):
        self._starttime: datetime = datetime.now(UTC)

        self.settings: Settings = settings
        self.paths: Paths = paths

        self.project_info: ProjectInfo = info
        self._env_loaded = False

    @property
    def setting_file(self) -> Path:
        return self.settings.file

    @property
    def names(self) -> Names:
        """Provide Names instance access with enforced dot access"""
        return self.settings.names

    @property
    def defaults(self) -> Defaults:
        """Provide Defaults instance access with enforced dot access"""
        return self.settings.defaults

    def save_settings(self, file: Path | None = None) -> None:
        """Provide access to save Setting file"""
        self.settings.save(file or self.setting_file)
        logger.info(f"Settings saved to: {self.setting_file}")

    def launch_log_setup(
        self, verbose: bool = False, quiet: bool = False
    ) -> Log:
        """Use Param with overrides for log setup and store applied param"""
        runtime_param = self.settings.log.with_overrides(
            verbose=verbose, quiet=quiet
        )
        self.log_result: Log = setup_logging(runtime_param)
        return self.log_result

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

    def from_env(self, key: str) -> str:
        """Ensure .env is loaded, get env var with key or raise Error"""

        if not self._env_loaded:
            load_dotenv(self.paths.dot_env())
            self._env_loaded = True

        if (var := os.getenv(key)) is not None:
            return var

        raise ValueError(f"Missing {key=} in os.env despite loaded .env")

    def __str__(self) -> str:  # TODO: apply utils.view
        return cls_name(self)

    def __repr__(self) -> str:  # TODO: apply utils.view
        members: list = [self.settings, self.paths, self.defaults, self.names]
        return f"{self}[{', '.join(cls_name(m) for m in members)}]"

    @classmethod
    def bootstrap(
        cls,
        settings_cls: type[Settings] | None = None,
        paths_cls: type[Paths] | None = None,
        setting_file: Path | None = None,
        project_name: str | None = None,
        project_root: Path | None = None,
        home_setup: HomeSetup = HomeSetup.GLOBAL,
    ) -> Self:

        info: ProjectInfo = ProjectInfo.collect(home_setup, project_name)
        homes: Homes = SstHomes.from_setup(home_setup, project_root, info.name)

        config_file: Path = setting_file or homes.config / "settings.json"

        settings_cls: type[Settings] = settings_cls or SstSettings
        settings: Settings = (
            settings_cls.load(file=config_file)
            if config_file.exists()
            else settings_cls(file=config_file)
        )
        paths_cls: type[Paths] = paths_cls or SstPaths
        paths: Paths = paths_cls(settings.defaults, settings.names, homes)

        return cls(settings, paths, info)


if TYPE_CHECKING:
    _instance_check: Config = ConfigManager.bootstrap()
    _class_check: type[Config] = ConfigManager
