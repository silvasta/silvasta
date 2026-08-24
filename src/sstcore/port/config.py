"""
Define the Shape of the Config Pipeline and Management

-
"""

# NEXT: copy docstrings here

__all__: list[str] = [
    "Config",
    "LogData",
    #
    "Settings",
    "Paths",
    "Defaults",
    "Names",
    "Homes",
    #
    "ProjectInformation",
]

from enum import StrEnum, auto
from pathlib import Path
from typing import Any, Protocol, Self

from .view import Stringable


class ProjectInformation(Protocol):
    """Collect Data and forward to Display"""

    @property
    def name(self) -> str:
        """Pyproject.toml Project Name"""

    @property
    def version(self) -> str:
        """Pyproject.toml Project Version"""


class Defaults(Protocol):
    @property
    def dot_env_content(self) -> str: ...
    @property
    def timestamp_format(self) -> str: ...


class Names(Protocol):
    def summary_file(
        self, day: Stringable = "", suffix: str = "md"
    ) -> str: ...
    @property
    def plot_dir(self) -> str: ...
    @property
    def scanner_cache_file(self) -> str: ...


class LogData(Protocol):  # MOVE: maybe, but where?
    log_dir: Path  # TASK: sync with Homes,utils.log,etc

    @property
    def log_file(self) -> Path: ...
    @property
    def struct_log_file(self) -> Path: ...
    def with_overrides(self, verbose: bool, quiet: bool) -> LogData: ...


class Settings(Protocol):
    def __init__(self, file: Path, **data: Any) -> None: ...
    @property
    def file(self) -> Path: ...
    @property
    def defaults(self) -> Defaults: ...
    @property
    def names(self) -> Names: ...
    @property
    def log(self) -> LogData: ...
    @classmethod
    def load(cls, file: Path) -> Self: ...
    def save(self, file: Path) -> None: ...
    def touch(self) -> Any: ...


class HomeSetup(StrEnum):
    GLOBAL = auto()
    PROJECT = auto()
    LOCAL = auto()
    CUSTOM = auto()


class Homes(Protocol):
    @property
    def root(self) -> Path: ...
    @property
    def cache(self) -> Path: ...
    @property
    def config(self) -> Path: ...
    @property
    def data(self) -> Path: ...
    @property
    def log(self) -> Path: ...
    @property
    def state(self) -> Path: ...


class Paths(Protocol):
    def __init__(
        self, defaults: Defaults, names: Names, homes: Homes
    ) -> None: ...
    @property
    def _defaults(self) -> Defaults: ...
    @property
    def _names(self) -> Names: ...
    @property
    def _homes(self) -> Homes: ...

    # Paths
    @property
    def project_root(self) -> Path: ...
    @property
    def config_dir(self) -> Path: ...
    @property
    def log_dir(self) -> Path: ...
    @property
    def data_dir(self) -> Path: ...
    @property
    def plot_dir(self) -> Path: ...

    def dot_env(self) -> Path: ...
    @property
    def dot_env_unconfirmed(self) -> Path: ...
    def scanner_cache_file(self, scan_root: Path | None = None) -> Path: ...
    def summary_file(self, suffix: str = "md") -> Path: ...


class Config(Protocol):
    @property
    def defaults(self) -> Defaults: ...
    @property
    def names(self) -> Names: ...
    @property
    def settings(self) -> Settings: ...
    @property
    def setting_file(self) -> Path: ...
    @property
    def paths(self) -> Paths: ...
    @property
    def project_info(self) -> ProjectInformation: ...
    @property
    def log_result(self) -> LogData: ...

    def save_settings(self, file: Path | None = None) -> Any: ...
    def from_env(self, key: str) -> str: ...
    def launch_log_setup(
        self, verbose: bool = False, quiet: bool = False
    ) -> LogData: ...

    @classmethod
    def bootstrap(cls, *args, **kwargs) -> Self: ...
