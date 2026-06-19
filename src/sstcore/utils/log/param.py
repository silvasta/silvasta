from pathlib import Path
from typing import Self

from pydantic import BaseModel, Field

from ..path.search import any_root


class LogParam(BaseModel):
    """Handle Input Param for log and provide defaults"""

    # setup behaviour
    print_at_setup: bool = True
    setup_source: str = "Defaults: utils.log.LogParam"

    # dir and file
    log_dir: Path = Field(default_factory=any_root)
    log_filename: str = "debug.log"

    # runtime behaviour and file management
    log_level: str = "INFO"
    retention: str = "1 week"
    rotation: str = "5 MB"

    @property
    def log_file(self) -> Path:
        return self.log_dir / self.log_filename

    def with_source(self, source: str) -> Self:
        self.setup_source: str = source
        return self

    def attach_logname(self, name: str) -> Self:
        if stem := name.rstrip(".log").strip():
            self.log_filename = f"{stem}.log"
        return self


class LogSetupResult(BaseModel):
    """Collect applied Param for log and provide results"""

    print_at_setup: bool
    setup_source: str

    # Final Path that was taken (usually the composed from LogParam)
    log_file: Path | None

    # From LogParam
    log_level: str
    retention: str
    rotation: str

    @classmethod
    def from_param(
        cls, log_file: Path | None, selected_param: LogParam
    ) -> Self:
        return cls(
            print_at_setup=selected_param.print_at_setup,
            setup_source=selected_param.setup_source,
            log_file=log_file,
            log_level=selected_param.log_level,
            retention=selected_param.retention,
            rotation=selected_param.rotation,
        )
