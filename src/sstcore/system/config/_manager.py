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
from typing import TYPE_CHECKING, Self, Unpack

from dotenv import load_dotenv
from loguru import logger

from ...brick.labor import clsname
from ...brick.time import day_count
from ...port.config import (
    Config,
    Defaults,
    Homes,
    LogData,
    Names,
    Paths,
    ProjectInformation,
    Settings,
)
from ...port.link import portlink
from ...port.system import ConfigData, ConfigInput, ConfigLoader
from ...util.log import setup_logging
from ...util.path import ProjectInfo
from ._homes import SstHomes
from ._paths import SstPaths
from ._settings import SstSettings


@portlink(Config)
class ConfigManager[D: Defaults, N: Names, P: Paths, S: Settings]:
    def __init__(self, settings: S, paths: P, info: ProjectInfo):
        self._starttime: datetime = datetime.now(UTC)

        self.settings: S = settings
        self.paths: P = paths

        self.project_info: ProjectInfo = info
        self._env_loaded = False

    @classmethod
    def bootstrap(cls, **data: Unpack[ConfigInput]) -> Self:
        dto: ConfigData = ConfigData(**data)

        info: ProjectInformation = ProjectInfo.collect(dto.project_name)
        homes: Homes = SstHomes.from_setup(
            dto.home_setup, dto.project_root, info.name
        )
        settings_cls: type[S] = dto.settings(default=SstSettings)
        config_file: Path = dto.setting_file or homes.config / "settings.json"
        settings: S = (
            settings_cls.load(file=config_file)
            if config_file.exists()
            else settings_cls(file=config_file)
        )
        paths_cls: type[P] = dto.paths(default=SstPaths)
        paths: P = paths_cls(settings.defaults, settings.names, homes)

        return cls(settings, paths, info)

    def save_settings(self, file: Path | None = None) -> None:
        self.settings.save(file or self.settings.file)
        logger.info(f"Settings saved to: {self.settings.file}")

    @property
    def names(self) -> N:
        return self.settings.names

    @property
    def defaults(self) -> D:
        return self.settings.defaults

    def launch_log_setup(
        self, verbose: bool = False, quiet: bool = False
    ) -> LogData:
        param: LogData = self.settings.log.evolve(verbose=verbose, quiet=quiet)
        self.log_result: LogData = setup_logging(param)
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

    def from_env(self, key: str, default: str | None = None) -> str:
        if not self._env_loaded:  # LATER: this as Field!??
            load_dotenv(self.paths.dot_env())
            self._env_loaded = True
        if (var := os.getenv(key)) is not None:
            return var
        if default is None:
            raise ValueError(f"Missing {key=} in os.env despite loaded .env")
        return default

    def __str__(self) -> str:  # TODO: apply utils.view
        return clsname(self)

    def __repr__(self) -> str:  # TODO: apply utils.view
        members: list = [self.settings, self.paths, self.defaults, self.names]
        return f"{self}[{', '.join(clsname(m) for m in members)}]"


if TYPE_CHECKING:
    _loader: ConfigLoader = ConfigManager.bootstrap
    _instance_check: Config = ConfigManager.bootstrap()
    _class_check: type[Config] = ConfigManager
