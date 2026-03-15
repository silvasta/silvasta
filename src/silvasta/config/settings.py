from functools import singledispatchmethod
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from silvasta.utils.path import PathGuard, find_project_root


class BasePaths:
    """Resolves Path objects using the provided Names"""

    def __init__(self, names: "BaseNames"):
        self._names = names  # Store the reference to names
        self.project_root = find_project_root()

    @property
    def user_setting_file(self) -> Path:  # TODO: global config file to read from
        return self.data_dir / self._names.user_setting_file

    @property
    @PathGuard.dir
    def data_dir(self) -> Path:
        return self.project_root / self._names.data_dir

    @property
    @PathGuard.dir
    def plot_dir(self) -> Path:
        return self.project_root / self._names.plot_dir


class BaseNames(BaseSettings):
    # NOTE: maybe hold start time for unique naming of CLI run?
    # - no, better directly in ConfigManager!
    # - move timestamp to defaults? probably
    # - factory for timestamp applied to custom name?
    #   - maybe here but solve first TASK below
    timestamp_format: str = "%Y-%m-%d_%H-%M-%S"  # This is to create names and write
    data_dir: str = "data"
    plot_dir: str = "plots"
    user_setting_file: str = "user_settings.json"  # NOTE: think about naming

    # --- Schema CSV-File Name --- #

    # # TASK: create this in custom class, somehow adapter here?
    # - list of patterns and keys?
    # schema_file_pattern: str = "{name}_schema_columns.csv"
    # # Store the pattern, not the logic
    # schema_config_pattern: str = "{name}_schema_config.json"
    # NOTE: see file-analyzer for singledispatchmethod example


class BaseDefaults(BaseSettings):
    """Main settings — import this everywhere"""

    # Use in CLI to parse input dates
    input_date_formats: list[str] = ["%d-%m-%Y", "%Y-%m-%d"]


class Settings(BaseSettings):
    """Main settings collector"""

    names: BaseNames = Field(default_factory=BaseNames)
    defaults: BaseDefaults = Field(default_factory=BaseDefaults)
