from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from .home_setup import HomeSetup


class SstDefaults(BaseSettings):
    """Default configurations for project handling"""

    model_config = ConfigDict(extra="allow")
    project_version_fallback: str = "0.1.0"

    home_setup: HomeSetup = HomeSetup.PROJECT
    setting_update_length: int = 79

    dot_env_content: str = ""  # write default content if no .env found
    project_root_indicator: str = "pyproject.toml"

    timestamp_format: str = "%Y-%m-%d_%H-%M-%S"
    input_date_formats: list[str] = ["%d-%m-%Y", "%Y-%m-%d"]  # parse dates
