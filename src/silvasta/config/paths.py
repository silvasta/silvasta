from pathlib import Path
from typing import cast

from loguru import logger

from silvasta.utils import PathGuard
from silvasta.utils.path import recursive_root

from .defaults import HomeSetup, SstDefaults
from .names import SstNames


class SstPaths[TNames: SstNames, TDefaults: SstDefaults]:
    """Generates paths with the provided Names and Defaults"""

    def __init__(
        self,
        names: TNames | None = None,
        defaults: TDefaults | None = None,
    ):
        self._defaults: TDefaults = defaults or cast(TDefaults, SstDefaults())
        self._names: TNames = names or cast(TNames, SstNames())

        self.project_root: Path = self._check_local_root()

    def _check_local_root(self) -> Path:
        """Find project root or use CWD"""
        root: Path | None = recursive_root(
            path=Path.cwd(),
            indicator=self._defaults.project_root_indicator,
        )
        if root is not None:
            self.project_root_found = True

            return root

        if self._defaults.home_setup == HomeSetup.LOCAL:  # TEST: home swich
            logger.warning("No project root found -> defaut to: 'global'")
            self._defaults.home_setup: HomeSetup = HomeSetup.GLOBAL

        self.project_root_found = False

        return Path.cwd()

    @property
    @PathGuard.dir
    def data_dir(self) -> Path:
        return self.project_root / self._names.data_dir

    @property
    @PathGuard.dir
    def plot_dir(self) -> Path:
        return self.project_root / self._names.plot_dir

    @property
    @PathGuard.dir
    def log_dir(self) -> Path:
        return self.project_root / self._names.log_dir

    @property
    @PathGuard.file(default_content="", raise_error=False)
    def log_file(self) -> Path:
        return self.log_dir / self._names.log_file

    @property
    @PathGuard.dir
    def local_home_dir(self) -> Path:
        return self.data_dir / self._names.local_home_dir

    @property
    @PathGuard.dir
    def data_home(self) -> Path:
        return self._defaults.home_setup.data_home

    @property
    @PathGuard.dir
    def state_home(self) -> Path:
        return self._defaults.home_setup.state_home

    @property
    @PathGuard.dir
    def config_home(self) -> Path:
        return self._defaults.home_setup.config_home

    @property
    def dot_env(self) -> Path:
        path: Path = self.config_home / ".env"
        return PathGuard.file(
            path, default_content=self._defaults.dot_env_content
        )
