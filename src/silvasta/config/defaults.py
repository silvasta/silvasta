from enum import StrEnum, auto
from pathlib import Path
from typing import TypeVar

from loguru import logger
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

from silvasta.utils import PathGuard
from silvasta.utils.path import XdgHomes


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
                msg = f"not able to connect to {self.local_home_root=}"

            case HomeSetup.GLOBAL:
                if self.project_name:
                    return XdgHomes(target).path / self.project_name
                msg = f"not able to connect {self.project_name=} to XdgHomes"

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


class LogDefaults(BaseSettings):
    level: str = "INFO"
    retention: str = "1 month"
    rotation: str = "10 MB"


class SstDefaults(BaseSettings):
    """Default configurations for project handling"""

    model_config = ConfigDict(extra="allow")

    project_name: str = "silvasta"  # REMOVE:
    project_version_fallback: str = "0.1.0"
    log: LogDefaults = Field(default_factory=LogDefaults)
    # Used for writing default content if no .env found
    dot_env_content: str = ""
    # Setup for path generation
    project_root_indicator: str = "pyproject.toml"
    home_setup: HomeSetup = HomeSetup.LOCAL
    # Use in CLI to parse input dates
    timestamp_format: str = "%Y-%m-%d_%H-%M-%S"

    # LATER: check this, as well with cli.args input parser
    input_date_formats: list[str] = ["%d-%m-%Y", "%Y-%m-%d"]
