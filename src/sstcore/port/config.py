"""
Define the Shape of the Config Pipeline and Management

                                    DependencyLevel.sstcore.port[1]
"""

__all__: list[str] = [
    "Config",
    "LogData",
    "HomeSetup",
    #
    "Settings",
    "Paths",
    "Defaults",
    "Names",
    "Homes",
    #
    "ProjectInformation",
]

import typing as _typing
from enum import StrEnum as _StrEnum
from enum import auto as _auto
from pathlib import Path as _Path

from ._types import _Stringable


class ProjectInformation(_typing.Protocol):
    """Collect Data and forward to Display"""

    @property
    def name(self) -> str:
        """Pyproject.toml Project Name"""

    @property
    def version(self) -> str:
        """Pyproject.toml Project Version"""


class LogData(_typing.Protocol):
    """Handle Input Param for log and provide defaults"""

    log_to_console: bool
    log_to_file: bool
    log_to_json: bool

    log_level: str
    retention: str
    rotation: str

    @property
    def log_file(self) -> _Path:
        """Ensured _Path for regular logs (at least empty file)"""

    @property
    def struct_log_file(self) -> _Path:
        """Ensure _Path for structured logs (at least empty file)"""

    def evolve(self, verbose: bool, quiet: bool) -> _typing.Self:
        """Create new detached DTO with runtime overrides"""


class HomeSetup(_StrEnum):
    """Select Target HomeDir Location"""

    GLOBAL = _auto()
    PROJECT = _auto()
    LOCAL = _auto()
    CUSTOM = _auto()


class Homes(_typing.Protocol):
    """Calculate HomeDir Paths depending on HomeSetup

    - Global:
        Located at XDG_HOMES, e.g.:  ~/.config/NAME  or  ~/.local/share/NAME

    - Project:
        Located at project root default identifier is 'pyproject.toml'

    - Local:
        Located at given path or usually CWD
    """

    @property
    def root(self) -> _Path: ...
    @property
    def cache(self) -> _Path: ...
    @property
    def config(self) -> _Path: ...
    @property
    def data(self) -> _Path: ...
    @property
    def log(self) -> _Path: ...
    @property
    def state(self) -> _Path: ...


class Defaults(_typing.Protocol):
    """Default Configurations for Project Handling"""

    @property
    def dot_env_content(self) -> str:
        """Provide content to fill empty .env file"""

    @property
    def timestamp_format(self) -> str:
        """Provide format rule for timestamps"""


class Names(_typing.Protocol):
    """Static and Dynamic Names together with Parsing Tools"""

    @property
    def data_dir(self) -> str: ...
    @property
    def plot_dir(self) -> str: ...

    def summary_file(self, day: _Stringable = "", suffix: str = "md") -> str:
        """Define the Name Schema for the Scanner Summary File"""

    @property
    def scanner_cache_file(self) -> str:
        """Define the Name for the Local Scanner Cache File"""


class Paths[
    D: Defaults = Defaults,
    N: Names = Names,
](_typing.Protocol):
    """Generate Paths with Defaults, Names and Homes - Ensure with _PathGuard"""

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
    def project_root(self) -> _Path: ...
    @property
    def config_dir(self) -> _Path: ...
    @property
    def log_dir(self) -> _Path: ...
    @property
    def data_dir(self) -> _Path: ...
    @property
    def plot_dir(self) -> _Path: ...

    def dot_env(self) -> _Path:
        """Ensure '.env' File or create Template on Missing and Raise"""

    @property
    def dot_env_unconfirmed(self) -> _Path:
        """Provide raw calculated dot_env _Path without any checks"""

    def summary_file(self, suffix: str = "md") -> _Path:
        """Ensure unique File _Path for the Scanner Summary File"""

    def scanner_cache(self, root: _Path | None = None, suffix=".db") -> _Path:
        """Provide Scanner Cache Location"""


class Settings[
    D: Defaults = Defaults,
    N: Names = Names,
](_typing.Protocol):
    """Collect Components and Serialize to Setting File"""

    @property
    def file(self) -> _Path:
        """Setting File _Path - Needs initial Configuration"""

    def __init__(self, file: _Path, *, log: LogData):
        """Enable typing for BaseModel Settings"""

    @property
    def defaults(self) -> D: ...
    @property
    def names(self) -> N: ...
    @property
    def log(self) -> LogData: ...

    @classmethod
    def load(cls, file: _Path) -> _typing.Self:
        """Extract and validate current state from file"""

    def touch(self) -> _typing.Any:
        """Update datetime and check maxlen of saved updates"""

    def save(self, file: _Path) -> None:
        """Touch and save current status to json"""


class Config[
    D: Defaults = Defaults,
    N: Names = Names,
    P: Paths = Paths,
    S: Settings = Settings,
](_typing.Protocol):
    """Bundle Container and Factories and provide access as Singleton"""

    @classmethod
    def bootstrap(cls, *args, **kwargs) -> _typing.Self:
        """Collect all Data needed to Setup with all Components"""

    @property
    def settings(self) -> S:
        """Provide Settings by dot access: config.settings"""

    def save_settings(self, file: _Path | None = None) -> _typing.Any:
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

    def from_env(self, key: str, default: str | None = None) -> str:
        """Ensure .env is loaded and find EnvVar, default or raise Error"""
