from functools import singledispatchmethod
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from silvasta.utils.path import PathGuard, find_project_root


class BasePaths(BaseSettings):
    @property
    def project_root(self) -> Path:
        return find_project_root()

    @property
    def user_setting_file(self) -> Path:
        return self.data_dir / BaseNames.user_setting_file

    @property
    @PathGuard.dir
    def data_dir(self) -> Path:
        return self.project_root / BaseNames.data_dir

    @property
    @PathGuard.dir
    def plot_dir(self) -> Path:
        return self.project_root / BaseNames.plot_dir

    @PathGuard.dir  # REMOVE: probably, is this needed in baseclass?
    def data(self, module: str) -> Path:
        return self.data_dir / module

    @PathGuard.dir  # REMOVE: probably, is this needed in baseclass?
    def plot(self, module: str) -> Path:
        return self.plot_dir / module


class BaseNames(BaseSettings):
    # NOTE: maybe hold start time for unique naming of CLI run?
    timestamp: str = "%Y-%m-%d_%H-%M-%S"  # This is to create names and write
    data_dir: str = "data"
    plot_dir: str = "plots"
    user_setting_file: str = "user_settings.json"  # NOTE: think about naming

    # --- Schema CSV-File Name --- #

    # TODO: adapt
    # Store the pattern, not the logic
    schema_file_pattern: str = "{name}_schema_columns.csv"
    schema_config_pattern: str = "{name}_schema_config.json"

    # REMOVE:
    @singledispatchmethod
    def schema_file(self, arg) -> str:
        raise NotImplementedError(f"Cannot process {type(arg)=}")

    @schema_file.register
    def _(self, arg: str) -> str:
        """String input -> returns filename string"""
        return f"{arg}_schema_columns.csv"

    @schema_file.register
    def _(self, arg: Path) -> str:
        """Path input -> returns extracted name string"""
        name: str = arg.name.split("_")[0]
        if arg.name != self.schema_file(name):
            raise ValueError(f"Problem with {arg=}")
        return name

    # --- Schema JSON-Config Name --- #
    # REMOVE:
    @singledispatchmethod
    def schema_config(self, arg) -> str:
        raise NotImplementedError(f"Cannot process {type(arg)=}")

    @schema_config.register
    def _(self, arg: str) -> str:
        return f"{arg}_schema_config.json"

    @schema_config.register
    def _(self, arg: Path) -> str:
        name: str = arg.name.split("_")[0]
        if arg.name != self.schema_config(name):
            raise ValueError(f"Problem with {arg=}")
        return name


class BaseDefaults(BaseSettings):
    """Main settings — import this everywhere"""

    # Used in CLI to parse input dates
    input_date_formats: list[str] = ["%d-%m-%Y", "%Y-%m-%d"]

    # AI: so far sparse, but this will heavily be customized


class Settings(BaseSettings):
    """Main settings collector"""

    # AI: in project:
    # class ProjectSettings(Setting):
    #   ...override or extend  what needed
    names: BaseNames = Field(default_factory=BaseNames)
    paths: BasePaths = Field(default_factory=BasePaths)
    defaults: BaseDefaults = Field(default_factory=BaseDefaults)
