from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class SstDefaults(BaseSettings):
    """Default configurations for project handling"""

    model_config = ConfigDict(extra="allow")

    timestamp_format: str = "%Y-%m-%d_%H-%M-%S"
    input_date_formats: list[str] = ["%d-%m-%Y", "%Y-%m-%d"]  # parse dates
    dot_env_content: str = ""  # write default content if no .env found
