from enum import StrEnum, auto
from pathlib import Path
from typing import TypeVar

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings

from silvasta.utils import PathGuard
from silvasta.utils.path import XdgHomes


class SstNames(BaseSettings):
    """Default names and name factories for files and project"""

    project: str = ""
    # Directories in project root
    data_dir: str = "data"
    plot_dir: str = "plots"
    # Directories in data_dir
    local_home_dir: str = "homes"
    # File names
    setting_file: str = "settings.json"

    # TASK: create bidirectional name/path in custom class,
    # somehow integrate here?
    # - list of patterns and keys?
    # schema_file_pattern: str = "{name}_schema_columns.csv"
    # # Store the pattern, not the logic
    # schema_config_pattern: str = "{name}_schema_config.json"
    # -> see file-analyzer for singledispatchmethod example


class HomeSetup(StrEnum):
    LOCAL = auto()
    GLOBAL = auto()

    # TEST: homesetup

    def boot(
        self,
        local_home_root: Path | None = None,
        project_name: str | None = None,
    ):
        self.local_home_root: Path | None = local_home_root
        self.project_name: str | None = project_name

        match self:
            case HomeSetup.LOCAL:
                if self.local_home_root is None:
                    raise ValueError("Need local home root for local homes!")
            case HomeSetup.GLOBAL:
                if self.project_name is None:
                    raise ValueError("Need project_name for XdgHomes!")
        logger.debug(f"HomeSetup '{self}' booted successfully")

    def get_path(self, target: str) -> Path:
        """Generate path for target={config|state|share}"""
        match self:
            case HomeSetup.LOCAL:
                if self.local_home_root:
                    return self.local_home_root / target
                msg = "not able to connect to local_home_root"
            case HomeSetup.GLOBAL:
                if self.project_name:
                    return XdgHomes(target).path / self.project_name
                msg = "not able to connect project_name to XdgHomes"
        raise AttributeError(msg)

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


class SstDefaults(BaseSettings):
    """Default configurations for project handling"""

    timestamp_format: str = "%Y-%m-%d_%H-%M-%S"
    # Used for writing default content if no .env found
    dot_env_content: str = ""
    # Setup for path generation
    project_root_indicator: str = "pyproject.toml"
    home_setup: HomeSetup = HomeSetup.LOCAL
    # Use in CLI to parse input dates
    input_date_formats: list[str] = ["%d-%m-%Y", "%Y-%m-%d"]


class SstSettings(BaseSettings):
    """Default settings and names, written to and loaded from file"""

    names: SstNames = Field(default_factory=SstNames)
    defaults: SstDefaults = Field(default_factory=SstDefaults)


TSettings = TypeVar("TSettings", bound=SstSettings)
TNames = TypeVar("TNames", bound=SstNames)
TDefaults = TypeVar("TDefaults", bound=SstDefaults)
