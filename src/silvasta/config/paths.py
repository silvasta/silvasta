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

        # MOVE: to config.manager? see INFO below

        project_name_from_settings: str = self._names.project
        project_name_from_toml: str = (
            "" if self._recursive_root is None else pyproject_name()
        )
        msg = f"{project_name_from_settings=}, {project_name_from_toml=}"

        if project_name_from_settings != project_name_from_toml:
            logger.warning(msg)
        else:
            logger.debug(msg)

        if project_name_from_settings:  # Priority 1
            logger.debug(
                f"Using project_project_name: {project_name_from_settings=}"
            )
            return project_name_from_settings

        if project_name_from_toml:  # Priority 2
            logger.debug(
                f"Using project_project_name: {project_name_from_toml=}"
            )
            self._names.project: str = project_name_from_toml
            return project_name_from_toml

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
        # maybe display here but control and execution from ConfigManager
        return self.config_home / self._names.setting_file


TPaths = TypeVar("TPaths", bound=SstPaths)


def get_setting_file_path() -> Path:
    # INFO: used for cli.setup with the idea not to load entire config
    # - problems: still booting home setup, move to config.manager?
    # still issue when boot changes the path that printed with this function
    # - probably fine as it is now, maybe REMOVE this function if somehow possible,
    # directly import SstPaths and ().setting_file?
    return SstPaths().setting_file
