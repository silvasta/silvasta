from enum import StrEnum, auto
from pathlib import Path
from typing import TypeVar

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings

from silvasta.utils.path import XdgHomes


class BaseNames(BaseSettings):
    """Default names and name factories for files and project"""

    timestamp_format: str = "%Y-%m-%d_%H-%M-%S"
    # NOTE: maybe hold start time for unique naming of CLI run?
    # - no, better directly in ConfigManager!
    # - move timestamp to defaults? probably
    # - factory for timestamp applied to custom name?
    #   - maybe here but solve first TASK below

    # Directories in project root
    data_dir: str = "data"
    plot_dir: str = "plots"
    # Directories in data_dir
    local_home_dir: str = "homes"
    # File names
    user_setting_file: str = "user_settings.json"  # NOTE: think about naming

    # TODO: error for not setting?
    # - or load from pyproject_toml?
    # what if both exist? priority user_setting_file,except for default
    project: str = "DefineProjectName"

    # --- Schema CSV-File Name --- #

    # TASK: create bidirectional name/path in custom class,
    # somehow integrate here?
    # - list of patterns and keys?
    # schema_file_pattern: str = "{name}_schema_columns.csv"
    # # Store the pattern, not the logic
    # schema_config_pattern: str = "{name}_schema_config.json"
    # NOTE: see file-analyzer for singledispatchmethod example


class HomeSetup(StrEnum):
    LOCAL = auto()
    GLOBAL = auto()

    def get_path(
        self,
        target: str,
        root: Path | None = None,
        project_name: str | None = None,
    ) -> Path:
        """Generate path for target={config|state|share}"""
        match self:
            case HomeSetup.LOCAL:
                if root is None:
                    raise ValueError("Root for local home dir not defined!")
                return root / target
            case HomeSetup.GLOBAL:
                if root is not None:
                    # REMOVE: after test
                    logger.warning(f"Global home ignores: {root=}")
                if project_name is None:
                    raise ValueError("Need project_name for XdgHomes!")
                return XdgHomes(target).path / project_name


class BaseDefaults(BaseSettings):
    """Default configurations for project handling"""

    # Used for writing default content if no .env found
    dot_env_content: str = ""
    # Setup for path generation
    project_root_indicator: str = "pyproject.toml"
    home_setup: HomeSetup = HomeSetup.LOCAL
    # Use in CLI to parse input dates
    input_date_formats: list[str] = ["%d-%m-%Y", "%Y-%m-%d"]


class Settings(BaseSettings):
    """Default settings and names, written to and loaded from file"""

    names: BaseNames = Field(default_factory=BaseNames)
    defaults: BaseDefaults = Field(default_factory=BaseDefaults)


TSettings = TypeVar("TSettings", bound=Settings)
TNames = TypeVar("TNames", bound=BaseNames)
TDefaults = TypeVar("TDefaults", bound=BaseDefaults)
