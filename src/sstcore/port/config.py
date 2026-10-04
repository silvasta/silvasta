"""
Define the Shape of the Config Pipeline and Management

                                    DependencyLevel.sstcore.port[1]
"""

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

from .calling import Stringable


class ProjectInformation(Protocol):
    """Collect Data and forward to Display"""

    @property
    def name(self) -> str:
        """Pyproject.toml Project Name"""

    @property
    def version(self) -> str:
        """Pyproject.toml Project Version"""


class LogData(Protocol):
    """Handle Input Param for log and provide defaults"""

    log_to_console: bool
    log_to_file: bool
    log_to_json: bool

    log_level: str
    retention: str
    rotation: str

    @property
    def log_file(self) -> Path:
        """Ensured Path for regular logs (at least empty file)"""

    @property
    def struct_log_file(self) -> Path:
        """Ensure Path for structured logs (at least empty file)"""

    def evolve(self, verbose: bool, quiet: bool) -> Self:
        """Create new detached DTO with runtime overrides"""


class HomeSetup(StrEnum):
    """Select Target HomeDir Location"""

    GLOBAL = auto()
    PROJECT = auto()
    LOCAL = auto()
    CUSTOM = auto()


class Homes(Protocol):
    """Calculate HomeDir Paths depending on HomeSetup

    - Global:
        Located at XDG_HOMES, e.g.:  ~/.config/NAME  or  ~/.local/share/NAME

    - Project:
        Located at project root default identifier is 'pyproject.toml'

    - Local:
        Located at given path or usually CWD
    """

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


class Defaults(Protocol):
    """Default Configurations for Project Handling"""

    @property
    def dot_env_content(self) -> str:
        """Provide content to fill empty .env file"""

    @property
    def timestamp_format(self) -> str:
        """Provide format rule for timestamps"""


class Names(Protocol):
    """Static and Dynamic Names together with Parsing Tools"""

    @property
    def data_dir(self) -> str: ...
    @property
    def plot_dir(self) -> str: ...

    def summary_file(self, day: Stringable = "", suffix: str = "md") -> str:
        """Define the Name Schema for the Scanner Summary File"""

    @property
    def scanner_cache_file(self) -> str:
        """Define the Name for the Local Scanner Cache File"""


class Paths[D: Defaults, N: Names](Protocol):
    """Generate Paths with Defaults, Names and Homes - Ensure with PathGuard"""

    def __init__(self, defaults: D, names: N, homes: Homes) -> None:
        """Assemble the upgradeable specific components just here"""

    @property
    def _defaults(self) -> D:
        """Defaults already exposed by config (here is: config.paths)"""

    @property
    def _names(self) -> N:
        """Names already exposed by config (here is: config.paths)"""

    @property
    def homes(self) -> Homes:
        """Provide Paths relative but independent of HomeSetup"""

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

    def dot_env(self) -> Path:
        """Ensure '.env' File or create Template on Missing and Raise"""

    @property
    def dot_env_unconfirmed(self) -> Path:
        """Provide raw calculated dot_env Path without any checks"""

    def summary_file(self, suffix: str = "md") -> Path:
        """Ensure unique File Path for the Scanner Summary File"""

    def scanner_cache_file(self, scan_root: Path | None = None) -> Path:
        """Find Scanner Cache Location or provide new Path"""


class Settings[D: Defaults, N: Names](Protocol):
    """Collect Components and Serialize to Setting File"""

    @property
    def file(self) -> Path:
        """Setting File Path - Needs initial Configuration"""

    def __init__(self, file: Path): ...  # INFO: needed for typing!

    @property
    def defaults(self) -> D: ...
    @property
    def names(self) -> N: ...
    @property
    def log(self) -> LogData: ...

    @classmethod
    def load(cls, file: Path) -> Self:
        """Extract and validate current state from file"""

    def touch(self) -> Any:
        """Update datetime and check maxlen of saved updates"""

    def save(self, file: Path) -> None:
        """Touch and save current status to json"""


class Config[D: Defaults, N: Names, P: Paths, S: Settings](Protocol):
    """Bundle Container and Factories and provide access as Singleton"""

    @classmethod
    def bootstrap(cls, *args, **kwargs) -> Self:
        """Collect all Data needed to Setup with all Components"""

    @property
    def settings(self) -> S:
        """Provide Settings by dot access: config.settings"""

    def save_settings(self, file: Path | None = None) -> Any:
        """Save config to Settings with Names and Defaults"""

    @property
    def paths(self) -> P:
        """Provide Paths by dot access: config.paths"""

    @property
    def names(self) -> N:
        """Provide Names by dot access: config.names"""

    @property
    def defaults(self) -> D:
        """Provide Defaults by dot access: config.defaults"""

    @property
    def project_info(self) -> ProjectInformation:
        """Collect default or from toml/meta extracted ProjectInfo"""

    def launch_log_setup(self, verbose: bool, quiet: bool) -> LogData:
        """Load LogParam with overrides and launch Log(uru) Setup"""

    @property
    def log_result(self) -> LogData:
        """Collect applied Param and Result of Log(uru) Setup"""

    def from_env(self, key: str) -> str:
        """Ensure .env is loaded and find EnvVar, default or raise Error"""
