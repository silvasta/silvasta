from enum import StrEnum, auto
from pathlib import Path

from loguru import logger

from ..utils import PathGuard
from ..utils.path import XdgHomes, find_project_root


class HomeSetup(StrEnum):  # TEST: homesetup
    GLOBAL = auto()
    PROJECT = auto()
    LOCAL = auto()

    def boot(
        self, project_name: str | None = None, local_root: Path | None = None
    ):
        """Launch setup with something like init"""

        match self:
            case HomeSetup.GLOBAL:
                if project_name is None:
                    raise ValueError("Need project_name for XdgHomes!")
                self.project_name: str = project_name

            case HomeSetup.PROJECT:
                self.root: Path = find_project_root("pyproject.toml")

            case HomeSetup.LOCAL:
                if local_root is None:
                    logger.warning("Need local home root for local homes!")
                    self.root: Path = Path.cwd()
                else:
                    self.root: Path = local_root

        logger.debug(f"HomeSetup '{self}' booted successfully")

    @property
    @PathGuard.dir
    def data_home(self) -> Path:
        return self.get_path(target="share")

    @property
    @PathGuard.dir
    def state_home(self) -> Path:
        return self.get_path(target="state")

    @property
    @PathGuard.dir
    def config_home(self) -> Path:
        return self.get_path(target="config")

    def get_path(self, target: str) -> Path:
        """Generate path for target={config|state|share}"""

        match self:
            case HomeSetup.GLOBAL:
                if self.project_name:
                    return XdgHomes(target).path_from_os() / self.project_name
                raise AttributeError(f"Missing: {self.project_name=}")

            case HomeSetup.PROJECT | HomeSetup.LOCAL:
                if self.root:
                    return self.root / target
