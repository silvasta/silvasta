"""
Create global states that hold global states

                                                       DependencyLevel[0]
"""

from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any

from loguru import logger

from .._core import System
from ..boot import sst_bus_loader, sst_config_loader, sst_system_loader
from ..config import ConfigManager
from ..event import EventBus

# LATER: use bus and emit if avaliable?


class _GlobalState(StrEnum):
    """Govern the handling of global Singletons"""

    SYSTEM = auto()
    CONFIG = auto()
    BUS = auto()

    @property
    def state(self) -> _Singleton:
        """Provide corresponding global state"""
        match self:
            case self.SYSTEM:
                return _system
            case self.CONFIG:
                return _config
            case self.BUS:
                return _bus

    @property
    def fetch(self):
        """Provide corresponding global instance"""
        return self.state.fetch

    def load(self, override=False):
        """Launch default loader and ensure global instance"""

        if self.state and not override:
            logger.debug(f"Ignoring load of already set {self.value}")
            return

        match self:
            case self.SYSTEM:
                self.state.set(update=sst_system_loader()())
            case self.CONFIG:
                self.state.set(update=sst_config_loader()())
            case self.BUS:
                self.state.set(update=sst_bus_loader()())

    @classmethod
    def load_all(cls, override):
        """Launch all default loader and ensure global instances"""
        for member in cls:
            member.load(override)

    def reset(self):
        """Reset corresponding global instance"""
        self.state.set(update=None)

    @classmethod
    def reset_all(cls):
        """Reset all corresponding global instances"""
        for member in cls:
            member.state.set(update=None)

    def update(self, instance: Any):
        """Set new instance in corresponding global state"""
        return self.state.set(update=instance)

    def change(self, value: Any | None):
        """Set new Singleton or None in corresponding global state"""
        if value is None:
            self.reset()
        else:
            self.state.set(update=value)


@dataclass
class _Singleton[TypeG: Any]:
    """Structure the Acces for a global Singleton"""

    state: _GlobalState
    instance: TypeG | None = None

    def __bool__(self) -> bool:
        """Confirm if instance is set"""
        return self.instance is not None

    @property
    def fetch(self) -> TypeG:
        """Fetch Global State of TypeG"""
        if not self:
            message = f"No access to global {self.state} without bootstrap!"
            raise RuntimeError(message)
        logger.debug(f"provide cached {self.state}")
        return self.instance  # ty:ignore

    def set(self, *, update: TypeG | None) -> None:
        """Set Global State of TypeG"""

        if self and update is not None:
            message = f"Replacing global {self.state}: {self.instance!r}"
            logger.warning(message)

        self.instance: TypeG | None = update

        if update is None:
            logger.info(f"Global {self.state} set to 'None'")
        else:
            logger.info(f"New {self.state} set as global: {update!r}")


_system: _Singleton[System] = _Singleton(state=_GlobalState.SYSTEM)

_config: _Singleton[ConfigManager] = _Singleton(state=_GlobalState.CONFIG)

_bus: _Singleton[EventBus] = _Singleton(state=_GlobalState.BUS)
