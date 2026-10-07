"""
Shape the Blueprint for Functors acting in different Spaces

FunctorMeta
  - ...

"""

__all__: list[str] = [
    "FunctorMeta",
    "FunctorMetaData",
]

import sys
from typing import Any, NoReturn

from loguru import logger

from ....brick.field import MorphingField, StrategyField
from ....port.functor import ErrorPolicy
from ....port.link import portlink
from ....port.shape import Meta, MetaData
from ._base import SstMeta, SstMetaData


@portlink(MetaData)
class FunctorMetaData(SstMetaData):
    # NOTE: so far nothing interesting to add...
    """Collect Policy and input check"""


@portlink(Meta)
class FunctorMeta[MaybeUsefulT](SstMeta):
    """Create Blueprint for Active Functorials"""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: FunctorMetaData,
    ):

        # AI_TASK: here the wiring is very important!
        # - the emit will 100% be needed like this in other metaclasses
        # - most important for functor, StrategyField and MorphingField
        # - check if and how they attach when injected to __dict__ like that

        _emit = _find_mountable("emit", bases, namespace)
        namespace["emit"] = _emit or _default_emit

        _call = namespace.get("call", _default_call)
        namespace["call"] = StrategyField(_call)

        _catch = namespace.get("catch", _default_catch)
        namespace["catch"] = MorphingField(_catch)

        return super().__new__(mcs, name, bases, namespace, data)


def _find_mountable(name, /, bases, namespace) -> Any | None:
    if name in namespace:
        return namespace[name]
    for base in bases:
        if attr_from_base := getattr(base, name, None):
            return attr_from_base


def _default_call(*args, **kwargs):
    # AI: self, needed/required?
    raise AttributeError("Functor is Missing _call_!", args, kwargs)


def _default_catch(self, error: Exception, *_, **__) -> Any | NoReturn:
    # AI: self, needed/required?
    """Handle Function fail by Policy if Catch is not defined"""
    logger.critical(f"{self} failed: {error}")

    match self.error_policy:
        case ErrorPolicy.LOG_AND_CONTINUE:
            return None

        case ErrorPolicy.LOG_AND_EXIT:
            logger.error(f"Original error: {error}")
            sys.exit(self.exit_code)

        case ErrorPolicy.RE_RAISE:
            raise error


def _default_emit(self, *args, **kwargs) -> None:  # MOVE: metablocks
    # AI: self, needed/required?
    logger.debug(*args, **kwargs)
