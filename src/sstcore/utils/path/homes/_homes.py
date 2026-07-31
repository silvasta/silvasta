"""
Boot HomeSetup depending on Configuration and provide according Paths

- Global:
    Located at XDG_HOMES, e.g.:  ~/.config/NAME  or  ~/.local/share/NAME

- Project:
    Located at project root usually identified by pyproject.toml

- Local:
    Located at given path or usually CWD

Path composition according to schema below.
- In projects usually: root/data/*homes
                                                       DependencyLevel[1]
"""

from enum import StrEnum, auto
from pathlib import Path

from loguru import logger

from .._search import find_project_root, get_project_root
from ._xdg import XdgHomes

# TASK: HomeSetup - make it interchangeable at any time
# use detection from CWD, with some defaults
# IDEA: Use Enum or similar as guard of uniqueness and dispatch,
# - somehow paired with dataclass but able to boot all 3 together?
# -> so far too unstable and error prone...


class HomeSetup(StrEnum):
    GLOBAL = auto()
    PROJECT = auto()
    LOCAL = auto()

    def boot(
        self,
        project_name: str | None = None,  # needed for global setup
        project_root: Path | None = None,  # needed for project setup
        local_root: Path | None = None,  # needed for local setup
    ):
        """Launch setup with something like init"""

        self._project_name: str | None = project_name
        self._project_root: Path | None = project_root or find_project_root()

        self._local_root: Path | None = local_root

        match self:
            case HomeSetup.GLOBAL:
                if self._project_name is None:
                    raise AttributeError("Need project_name for XdgHomes!")

            case HomeSetup.PROJECT:
                if self._project_root is None:
                    logger.info("HomeSetup.PROJECT Boots with toml_search!")
                self._project_root: Path = project_root or get_project_root()

            case HomeSetup.LOCAL:
                if local_root is None:
                    logger.info("HomeSetup.LOCAL Boots at CWD!")

        if self._project_root is None:
            self._project_root: Path | None = find_project_root()
            logger.debug(f"set project_root to {Path.cwd()=}")

        if self._local_root is None:
            self._local_root: Path = Path.cwd()
            logger.debug(f"set local_root to {Path.cwd()=}")

        logger.debug(f"HomeSetup '{self}' booted successfully")

    @property
    def project_name(self) -> str:
        if not self._project_name:
            raise AttributeError("wrong boot")
        return self._project_name

    @property
    def project_root(self) -> Path:
        if not self._project_root:
            raise AttributeError("wrong boot")

        return self._project_root

    @property
    def root(self) -> Path:
        # NEXT:
        # TODO: auto switch to local
        match self:
            case self.PROJECT:
                return self.project_root
            case self.LOCAL:
                return self.local_root
        raise ValueError

    @property
    def local_root(self) -> Path:
        if not self._local_root:
            raise AttributeError("wrong boot")
        return self._local_root

    def home_path(self, target: str, to_homes="data") -> Path:
        """Generate path for target={config|state|share}"""

        match self:
            case HomeSetup.GLOBAL:
                return XdgHomes(target).path_from_os() / self.project_name

            case HomeSetup.PROJECT:
                return self.project_root / to_homes / "homes" / target

            case HomeSetup.LOCAL:
                return self.local_root / to_homes / "homes" / target

    @property
    def configs_dir(self) -> Path:
        match self:
            case self.PROJECT:
                return self.project_root / "configs"

            case self.GLOBAL | self.LOCAL:
                return self.config_home

    @property
    def log_dir(self) -> Path:
        match self:
            case self.PROJECT:
                return self.project_root / "logs"

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
