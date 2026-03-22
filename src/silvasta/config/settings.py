from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings

from silvasta.utils.path import PathGuard, XdgHomes, find_project_root


class BasePaths:
    """Resolves Path objects using the provided Names"""

    # INFO: TNames, TDefaults most likely needed

    def __init__(self, names: "BaseNames", defaults: "BaseDefaults"):
        self._names = names  # Store the reference to names
        self._defaults = defaults
        self.project_root = find_project_root()  # WARN: error not catched

        # TODO: self.project_root:
        # - if not avaliable -> swich to global
        # - if anyway global, don't search
        # check as well other cases and implement

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
        return self.data_dir / "homes"  # PARAM: makes sense in Names?

    @property
    @PathGuard.dir
    def config_home(self) -> Path:
        match self._defaults.home_setup:
            case "local":
                return self.local_home_dir / "config"
            case "global":
                return XdgHomes.CONFIG.path / self._names.project
            case _:
                raise AttributeError(f"Invalid: {self._defaults.home_setup=}")

    @property
    @PathGuard.dir
    def data_home(self) -> Path:
        match self._defaults.home_setup:
            case "local":
                return self.local_home_dir / "share"
            case "global":
                return XdgHomes.DATA.path / self._names.project
            case _:
                raise AttributeError(f"Invalid: {self._defaults.home_setup=}")

    @property
    @PathGuard.dir
    def state_home(self) -> Path:
        match self._defaults.home_setup:
            case "local":
                return self.local_home_dir / "state"
            case "global":
                return XdgHomes.STATE.path / self._names.project
            case _:
                raise AttributeError(f"Invalid: {self._defaults.home_setup=}")

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


class BaseNames(BaseSettings):
    timestamp_format: str = "%Y-%m-%d_%H-%M-%S"
    # NOTE: maybe hold start time for unique naming of CLI run?
    # - no, better directly in ConfigManager!
    # - move timestamp to defaults? probably
    # - factory for timestamp applied to custom name?
    #   - maybe here but solve first TASK below
    data_dir: str = "data"
    plot_dir: str = "plots"
    user_setting_file: str = "user_settings.json"  # NOTE: think about naming

    project: str = "DefineProjectName"  # TODO: error for not setting?

    # --- Schema CSV-File Name --- #

    # TASK: create bidirectional name/path in custom class,
    # somehow integrate here?
    # - list of patterns and keys?
    # schema_file_pattern: str = "{name}_schema_columns.csv"
    # # Store the pattern, not the logic
    # schema_config_pattern: str = "{name}_schema_config.json"
    # NOTE: see file-analyzer for singledispatchmethod example


class BaseDefaults(BaseSettings):
    """Main settings — import this everywhere"""

    dot_env_content: str = ""
    home_setup: Literal["local", "global"] = "local"  # LATER: make Enum?
    # Use in CLI to parse input dates
    input_date_formats: list[str] = ["%d-%m-%Y", "%Y-%m-%d"]


class Settings(BaseSettings):
    """Main settings collector"""

    names: BaseNames = Field(default_factory=BaseNames)
    defaults: BaseDefaults = Field(default_factory=BaseDefaults)
