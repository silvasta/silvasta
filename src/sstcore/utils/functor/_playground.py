from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from ...port.event import Event
from ...port.functor import ErrorPolicy, Functorial
from ...port.pathguard import SyncMode, TransferStrategic
from ._base import Functor


def dummy_good(source: Path, target: Path, mode=SyncMode.IGNORE):
    pass


def dummy_bad(source: str, mode=SyncMode.IGNORE):
    pass


# REMOVE: after established in PathGuard
class TransferStrategy(Functor[[Path, Path, SyncMode], Path]):
    error_policy: ErrorPolicy = ErrorPolicy.LOG_AND_CONTINUE
    exit_code: int = 1


if TYPE_CHECKING:
    _transfer: Functorial = TransferStrategy.from_func(dummy_good)
    _strategy: type[Functorial] = TransferStrategy

    _transfer: TransferStrategic = TransferStrategy.from_func(dummy_good)
    _strategy: type[TransferStrategic] = TransferStrategy

    _transfer: Functorial = TransferStrategy.from_func(dummy_bad)
    _strategy: type[Functorial] = TransferStrategy

    _transfer: TransferStrategic = TransferStrategy.from_func(dummy_bad)
    _strategy: type[TransferStrategic] = TransferStrategy

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### TESTS
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@dataclass(frozen=True)
class _EventHandler(Functor[[Event], None]):
    """First ideas - TESTING"""

    fail_loud: bool = False

    def __call__(self, event: Event) -> None:
        try:
            self.func(event)
        except Exception as e:
            if self.fail_loud:
                raise RuntimeError(f"Critical fail in {self}") from e
            logger.error(f"{self} failed for '{event.name}': {e}")


@dataclass(frozen=True)
class _ErrorHandler[Error: BaseException](Functor[[Error], None]):
    """First ideas - TESTING"""

    exception_type: type[Error]
    exit_code: int = 1
