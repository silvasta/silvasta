from pathlib import Path
from typing import Any, Self

from pydantic import BaseModel, Field

from ..path import PathGuard, any_root


class LogParam(BaseModel):
    """Handle Input Param for log and provide defaults"""

    # Setup behaviour
    print_at_setup: bool = False

    # Toggles (The 3 outputs you need to control)
    log_to_console: bool = True
    log_to_file: bool = True
    log_to_json: bool = True

    # Directories and names
    log_dir: Path = Field(default_factory=any_root)
    log_file_stem: str = "debug"
    file_suffix: str = ".log"
    json_suffix: str = ".jsonl"

    # Runtime behaviour and file management
    log_level: str = "INFO"
    retention: str = "1 week"
    rotation: str = "5 MB"

    @property
    @PathGuard.file(default_content="", raise_error=False)
    def log_file(self) -> Path:
        """Get ensured Path for regular logs (at least empty file)"""
        return self.log_dir / f"{self.log_file_stem}{self.file_suffix}"

    @property
    @PathGuard.file(default_content="", raise_error=False)
    def struct_log_file(self) -> Path:
        """Get ensured Path for structured logs (at least empty file)"""
        return self.log_dir / f"{self.log_file_stem}{self.json_suffix}"

    def with_overrides(
        self, verbose: bool = False, quiet: bool = False
    ) -> Self:
        """Create new detached DTO for Runtime overrides"""
        updates: dict[str, Any] = {}
        if verbose:
            updates["log_level"] = "DEBUG"
        if quiet:
            updates["log_to_console"] = False
        return self.model_copy(update=updates)
