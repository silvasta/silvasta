from pathlib import Path
from typing import Generic, TypeVar, cast

from loguru import logger

from silvasta.utils import PathGuard
from silvasta.utils.path import pyproject_name, recursive_root

from .settings import HomeSetup, SstDefaults, SstNames, TDefaults, TNames


class SstPaths(Generic[TNames, TDefaults]):
    """Resolves Path objects using the provided Names"""

    def __init__(
        self,
        names: TNames | None = None,
        defaults: TDefaults | None = None,
    ):
        # WARN: class Paths(BasePaths[TNames, TDefaults])
        # - badly assigned types here will cause problems
        # - errors and warnings of type checker will be shadowed

        self._names: TNames = names or cast(TNames, SstNames())
        self._defaults: TDefaults = defaults or cast(TDefaults, SstDefaults())

        self.project_root: Path = self._check_local_root()
        project_name: str = self._check_project_name()

        self._defaults.home_setup.boot(
            local_home_root=self.local_home_dir,
            project_name=project_name,
        )

    def _check_project_name(self) -> str:

        name_from_settings: str = self._names.project
        name_from_toml: str = (
            "" if self._recursive_root is None else pyproject_name()
        )
        if name_from_settings and name_from_toml:
            logger.warning(f"{name_from_settings=} differs {name_from_toml=}")

        if name_from_settings:
            logger.debug(f"Using project_name: {name_from_settings=}")
            return name_from_settings

        if name_from_toml:
            logger.debug(f"Using project_name: {name_from_toml=}")
            self._names.project: str = name_from_toml
            return name_from_toml

        logger.warning("No project_name defined!")
        return "DefineProjectName"

    def _check_local_root(self) -> Path:
        self._recursive_root: Path | None = recursive_root(
            path=Path.cwd(),
            indicator=self._defaults.project_root_indicator,
        )
        if self._recursive_root is not None:
            return self._recursive_root

        # TEST: home swich
        if self._defaults.home_setup == HomeSetup.LOCAL:
            logger.warning("No project root found -> defaut to: 'global'")
            self._defaults.home_setup: HomeSetup = HomeSetup.GLOBAL

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

    @property
    def setting_file(self) -> Path:
        # LATER: iterate over possible config locations at init?
        # maybe some execution here but control from ConfigManager
        return self.config_home / self._names.setting_file


TPaths = TypeVar("TPaths", bound=SstPaths)
