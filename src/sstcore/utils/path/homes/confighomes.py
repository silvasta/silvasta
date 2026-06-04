from enum import StrEnum, auto
from pathlib import Path

from loguru import logger

from ..utils.path import XdgHomes, find_project_root


class HomeSetup(StrEnum):  # TEST: homesetup
    GLOBAL = auto()
    PROJECT = auto()
    LOCAL = auto()

    def boot(
        self,
        project_name: str | None = None,  # needed for global setup
        project_root_indicator: str = "pyproject.toml",  # needed for project setup
        project_root: Path | None = None,  # needed for local setup
    ):
        """Launch setup with something like init"""

        match self:
            case HomeSetup.GLOBAL:
                if project_name is None:
                    raise AttributeError("Need project_name for XdgHomes!")
                self.project_name: str = project_name

            case HomeSetup.PROJECT:
                project_root: Path = find_project_root(project_root_indicator)

            case HomeSetup.LOCAL:
                if project_root is None:
                    logger.warning("HomeSetup boots without provided Path!")

        if project_root is None:
            self.root: Path = Path.cwd()
            logger.debug(f"Setting Project root to {Path.cwd()=}")
        else:
            self.root: Path = project_root

        logger.debug(f"HomeSetup '{self}' booted successfully")

    def home_path(self, target: str, to_homes="data") -> Path:
        """Generate path for target={config|state|share}"""

        match self:
            case HomeSetup.GLOBAL:
                if self.project_name:
                    return XdgHomes(target).path_from_os() / self.project_name
                raise AttributeError(f"Missing: {self.project_name=}")

            case HomeSetup.PROJECT | HomeSetup.LOCAL:
                # PARAM: to_homes, maybe as class attribute
                return self.root / to_homes / "homes" / target

    @property
    def configs_dir(self) -> Path:
        match self:
            case self.PROJECT:
                return self.root / "configs"

            case self.GLOBAL | self.LOCAL:
                return self.config_home

    @property
    def log_dir(self) -> Path:
        match self:
            case self.PROJECT:
                return self.root / "logs"

            case self.GLOBAL | self.LOCAL:
                return self.state_home / "logs"

    @property
    def config_home(self) -> Path:
        return self.home_path(target="config")

    @property
    def state_home(self) -> Path:
        return self.home_path(target="state")

    @property
    def data_home(self) -> Path:
        return self.home_path(target="share")
