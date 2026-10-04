"""
Provide DTO for Bootstrap Pipeline

- Ensure proper communication with config, settings and log
  - stored in config.Settings -> settings.json
                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "LogParam",
]

from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

from pydantic import BaseModel, Field

from ...port.config import LogData
from ...port.link import portlink
from ..path import any_root
from ..path.guard import PathGuard


@portlink(LogData)
class LogParam(BaseModel):
    # Toggles (The 3 outputs you need to control)
    log_to_console: bool = True
    log_to_file: bool = True
    log_to_json: bool = True

    # Setup behaviour
    print_at_setup: bool = False

    # Runtime behaviour and file management
    log_level: str = "INFO"
    retention: str = "1 week"
    rotation: str = "5 MB"

    # Directories and names
    log_dir: Path = Field(default_factory=any_root)  # TODO:
    log_file_stem: str = "debug"
    file_suffix: str = ".log"
    json_suffix: str = ".jsonl"

    @property
    @PathGuard.file(default_content="", raise_error=False)
    def log_file(self) -> Path:
        return self.log_dir / f"{self.log_file_stem}{self.file_suffix}"

    @property
    @PathGuard.file(default_content="", raise_error=False)
    def struct_log_file(self) -> Path:
        return self.log_dir / f"{self.log_file_stem}{self.json_suffix}"

    def evolve(self, verbose: bool = False, quiet: bool = False) -> Self:
        updates: dict[str, Any] = {}
        if verbose:
            updates["log_level"] = "DEBUG"
        if quiet:
            updates["log_to_console"] = False
        return self.model_copy(update=updates)


if TYPE_CHECKING:
    _instance_check: LogData = LogParam()
    _class_check: type[LogData] = LogParam
