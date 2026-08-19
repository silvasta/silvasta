"""
Provide defaults and basic access for XDG Homes in system environment

                                                       DependencyLevel[0]
"""

from typing import TYPE_CHECKING, Self

from sstcore.port.config import Homes

from ._search import get_project_root

__all__: list[str] = [
    "XdgHomes",
    "XdgDefaults",
]

import os
from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path


@dataclass
class XdgDefaults:
    """Define fallback location in case env_var call failed"""

    data: str = ".local/share"
    state: str = ".local/state"
    config: str = ".config"
    cache: str = ".cache"
    bin: str = ".local/bin"


class XdgHomes(StrEnum):
    """Manage access to XDG env vars and compose specific Home Paths"""

    CACHE = auto()
    CONFIG = auto()
    DATA = auto()
    STATE = auto()

    @property
    def env_var(self) -> str:
        """Format string with member env variable name"""
        return f"XDG_{self.name}_HOME"

    def path_from_os(self, defaults: XdgDefaults | None = None) -> Path:
        """Find Path in env vars or fallback to defaults"""

        if env_val := os.getenv(self.env_var):
            return Path(env_val).expanduser().resolve()

        return self.default_path(defaults)

    def default_path(self, defaults: XdgDefaults | None = None) -> Path:
        """Default to User Home and apply Default Location"""

        defaults: XdgDefaults = defaults or XdgDefaults()

        mapping: dict = {
            self.CACHE: defaults.cache,
            self.CONFIG: defaults.config,
            self.DATA: defaults.data,
            self.STATE: defaults.state,
        }
        return Path.home() / mapping[self]


@dataclass
class HomeDirs:
    """
    Create HomeDir Paths depending on Configuration

    - Global:
        Located at XDG_HOMES, e.g.:  ~/.config/NAME  or  ~/.local/share/NAME

    - Project:
        Located at project root usually identified by pyproject.toml

    - Local:
        Located at given path or usually CWD
    """

    root: Path
    cache: Path
    config: Path
    data: Path
    log: Path
    state: Path

    @classmethod
    def at_global(
        cls, project_name: str, project_root: Path | None = None
    ) -> Self:
        return cls(
            root=project_root or Path.cwd(),
            cache=XdgHomes.CACHE.path_from_os() / project_name,
            config=(XdgHomes.CONFIG.path_from_os() / project_name),
            data=XdgHomes.DATA.path_from_os() / project_name,
            log=XdgHomes.STATE.path_from_os() / project_name / "logs",
            state=XdgHomes.STATE.path_from_os() / project_name,
        )

    @classmethod
    def at_project(cls, project_root: Path | None = None) -> Self:
        return cls(
            root=(root := (project_root or get_project_root())),
            cache=root / "cache",
            config=root / ".config",
            data=root / "data",
            log=root / "logs",
            state=root / "state",
        )

    @classmethod
    def at_local(cls, local_root: Path | None = None) -> Self:
        return cls(
            root=(root := (local_root or (Path.cwd() / ".sstcore"))),
            cache=root / "cache",
            config=root / "config",
            data=root / "data",
            log=root / "logs",
            state=root / "state",
        )


if TYPE_CHECKING:
    _instance_check: Homes = HomeDirs(**dict())
    _class_check: type[Homes] = HomeDirs
