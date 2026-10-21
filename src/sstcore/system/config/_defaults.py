"""
Provide Container for Defaults and Params

- Serialize with Settings and distribute with ConfigManager
- Provide (minimal) subset of default defaults and for SstPaths
                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "SstDefaults",
]


from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from ...port.config import Defaults
from ...port.link import portlink


@portlink(Defaults)
class SstDefaults(BaseSettings):
    model_config = ConfigDict(extra="allow")

    timestamp_format: str = "%Y-%m-%d_%H-%M-%S"
    input_date_formats: list[str] = ["%d-%m-%Y", "%Y-%m-%d"]  # parse dates
    dot_env_content: str = ""
