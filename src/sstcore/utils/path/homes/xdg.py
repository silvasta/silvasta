# TODO: explain

import os
from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path


@dataclass
class XdgDefaults:
    # TODO: explain
    data: str = ".local/share"
    state: str = ".local/state"
    config: str = ".config"
    cache: str = ".cache"
    bin: str = ".local/bin"


class XdgHomes(StrEnum):
    # TODO: explain
    DATA = auto()
    STATE = auto()
    CONFIG = auto()
    CACHE = auto()
    BIN = auto()

    @property
    def env_var(self) -> str:
        """BIN has no official XDG_BIN_HOME variable, but lets try"""
        if self == XdgHomes.BIN:
            return "XDG_BIN_HOME"
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
            XdgHomes.DATA: defaults.data,
            XdgHomes.STATE: defaults.state,
            XdgHomes.CONFIG: defaults.config,
            XdgHomes.CACHE: defaults.cache,
            XdgHomes.BIN: defaults.bin,
        }
        return Path.home() / mapping[self]
