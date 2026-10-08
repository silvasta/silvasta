"""
Shape the Blueprint for Functors acting in different Spaces

FunctorMeta
  - ...

"""

__all__: list[str] = [
    "FunctorMeta",
    "FunctorMetaData",
]

from typing import Any, NoReturn

from loguru import logger

from ....brick.field import MethodFieldEngine, MorphingField, StrategyField
from ....brick.none import sentinel
from ....port.link import portlink
from ....port.shape import Meta, MetaData
from ._meta_base import SstMeta, SstMetaData

_MISSING = sentinel("MISSING")


@portlink(MetaData)
# NOTE: so far nothing interesting to add...
class FunctorMetaData(SstMetaData):
    """Collect Policy and input check"""


@portlink(Meta)
class FunctorMeta(SstMeta):
    """Create Blueprint for Active Functorials"""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: FunctorMetaData,
    ):
        for key, value in list(namespace.items()):
            field_kind: Any | type[MethodFieldEngine] = getattr(
                value, "__field_kind__", None
            )
            if field_kind is not None and not isinstance(
                value,
                MethodFieldEngine,  # CHECK: againg in _install??
            ):
                namespace[key] = field_kind(value, bind_to_self=True)

        _install(namespace, bases, "call", StrategyField, _default_call)
        _install(namespace, bases, "catch", MorphingField, _default_catch)
        _install(namespace, bases, "emit", MorphingField, _default_emit)

        return super().__new__(mcs, name, bases, namespace, data)


def _install(namespace, bases, name, field_cls, default, /):
    existing = namespace.get(name, _MISSING)

    if isinstance(existing, MethodFieldEngine):
        return

    field_kind: Any | None = getattr(existing, "__field_kind__", None)
    if field_kind is not None and not isinstance(existing, MethodFieldEngine):
        namespace[name] = field_kind(existing, bind_to_self=True)
        return

    if callable(existing):
        namespace[name] = field_cls(existing, bind_to_self=True)
        return

    for base in bases:
        attr: Any = base.__dict__.get(name)
        if isinstance(attr, MethodFieldEngine):
            namespace[name] = field_cls(
                attr.target_func, bind_to_self=attr.bind_to_self
            )
            return
        if callable(attr):
            namespace[name] = field_cls(attr, bind_to_self=True)
            return

    namespace[name] = field_cls(default, bind_to_self=True)


def _default_call(self, *args, **kwargs):
    raise AttributeError("Functor is Missing: [ _call_ ]!", self, args, kwargs)


def _default_catch(self, error: Exception, *_, **__) -> Any | NoReturn:
    logger.critical(f"{self} failed: {error}")
    raise error


def _default_emit(self, *args, **kwargs) -> None:  # MOVE: global meta defaults
    logger.debug(*args, sender=str(self), **kwargs)
