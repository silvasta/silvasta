from typing import TypeVar

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class SstNames(BaseSettings):
    """Default names and name factories for files and project"""

    model_config = ConfigDict(extra="allow")

    project: str

    # Values for master config file!
    setting_file: str = "settings.json"  # needed?
    _log_file_name: str = ""
    # Directories in project root
    data_dir: str = "data"
    plot_dir: str = "plots"
    log_dir: str = "plots"
    # Directories in data_dir
    local_home_dir: str = "homes"

    @property
    def log_file(self) -> str:
        return (
            self._log_file_name
            if self._log_file_name
            else f"{self.project}.log"
        )

    # TASK: create bidirectional name/path in custom class,
    # somehow integrate here?
    # - list of patterns and keys?
    # schema_file_pattern: str = "{name}_schema_columns.csv"
    # # Store the pattern, not the logic
    # schema_config_pattern: str = "{name}_schema_config.json"
    # -> see file-analyzer for singledispatchmethod example


TNames = TypeVar("TNames", bound=SstNames)
