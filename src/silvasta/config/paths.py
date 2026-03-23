from pathlib import Path
from typing import Generic, TypeVar, cast

from loguru import logger

from silvasta.utils.path import PathGuard, recursive_root

from .settings import BaseDefaults, BaseNames, HomeSetup, TDefaults, TNames


class BasePaths(Generic[TNames, TDefaults]):
    """Resolves Path objects using the provided Names"""

    def __init__(
        self,
        names: TNames | None = None,
        defaults: TDefaults | None = None,
    ):
        self._names: TNames = names or cast(TNames, BaseNames())
        # WARN: class Paths(BasePaths[TNames, TDefaults])
        # -> badly assigned types here will cause problems, hidden to type checker
        self._defaults: TDefaults = defaults or cast(TDefaults, BaseDefaults())

        self.project_root: Path = self._set_local_root()

    def _set_local_root(self) -> Path:
        if root := recursive_root(
            path=Path.cwd(),
            indicator=self._defaults.project_root_indicator,
        ):
            return root

        if self._defaults.home_setup == HomeSetup.LOCAL:
            self._defaults.home_setup: HomeSetup = HomeSetup.GLOBAL
            logger.warning("No project root found -> defaut: 'global' ")
        return Path.cwd()

    @property
    @PathGuard.dir
    def data_dir(self) -> Path:
        # TODO: handle no project root
        return self.project_root / self._names.data_dir

    @property
    @PathGuard.dir
    def plot_dir(self) -> Path:
        # TODO: handle no project root
        return self.project_root / self._names.plot_dir

    @property
    @PathGuard.dir
    def local_home_dir(self) -> Path:
        # TODO: handle no project root
        return self.data_dir / self._names.local_home_dir

    @property
    @PathGuard.dir
    def data_home(self) -> Path:
        return self._defaults.home_setup.get_path(
            target="share", root=self.local_home_dir
        )  # INFO: root ignored for global, more explicit?

    @property
    @PathGuard.dir
    def state_home(self) -> Path:
        return self._defaults.home_setup.get_path(
            target="state", root=self.local_home_dir
        )  # INFO: root ignored for global, more explicit?

    @property
    @PathGuard.dir
    def config_home(self) -> Path:
        return self._defaults.home_setup.get_path(
            target="config", root=self.local_home_dir
        )  # INFO: root ignored for global, more explicit?

    @property
    def dot_env(self) -> Path:
        path: Path = self.config_home / ".env"
        return PathGuard.file(
            path, default_content=self._defaults.dot_env_content
        )

    @property
    def user_setting_file(self) -> Path:
        # TODO: global config file to read from
        return self.data_dir / self._names.user_setting_file


TPaths = TypeVar("TPaths", bound=BasePaths)
