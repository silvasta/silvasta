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

from ....brick.field import MethodFieldEngine, MorphingField, StrategyField
from ....brick.none import sentinel
from ....port.functor import ErrorPolicy
from ....port.link import portlink
from ....port.shape import Meta, MetaData
from ._base import SstMeta, SstMetaData

_MISSING = sentinel("MISSING")


@portlink(MetaData)
class FunctorMetaData(SstMetaData):
    # NOTE: so far nothing interesting to add...
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
                value, MethodFieldEngine
            ):
                namespace[key] = field_kind(value, binds_instance=True)

        _install(namespace, bases, "call", StrategyField, _default_call)
        _install(namespace, bases, "catch", MorphingField, _default_catch)
        _install(namespace, bases, "emit", MorphingField, _default_emit)

        return super().__new__(mcs, name, bases, namespace, data)


def _find_mountable(name, /, bases, namespace) -> Any | None:
    if name in namespace:
        return namespace[name]
    for base in bases:
        if attr_from_base := getattr(base, name, None):
            return attr_from_base


def _install(namespace, bases, name, field_cls, default, /):
    existing = namespace.get(name, _MISSING)

    if isinstance(existing, MethodFieldEngine):
        return

    field_kind = getattr(existing, "__field_kind__", None)
    if field_kind is not None and not isinstance(existing, MethodFieldEngine):
        namespace[name] = field_kind(existing, binds_instance=True)
        return

    if callable(existing):
        namespace[name] = field_cls(existing, binds_instance=True)
        return

    for base in bases:
        attr = base.__dict__.get(name)
        if isinstance(attr, MethodFieldEngine):
            namespace[name] = field_cls(
                attr.target_func, binds_instance=attr.binds_instance
            )
            return
        if callable(attr):
            namespace[name] = field_cls(attr, binds_instance=True)
            return

    namespace[name] = field_cls(default, binds_instance=True)


def _default_call(self, *args, **kwargs):
    raise AttributeError("Functor is Missing _call_!", self, args, kwargs)


def _default_catch(self, error: Exception, *_, **__) -> Any | NoReturn:
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


def _default_emit(self, *args, **kwargs) -> None:
    logger.debug(*args, sender=str(self), **kwargs)


#  LINE: -- Other Ideas -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@portlink(Meta)
class _G3FunctorMeta(SstMeta):
    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: FunctorMetaData,
    ):
        if "emit" not in namespace:
            namespace["emit"] = (
                _find_mountable("emit", bases, namespace) or _default_emit
            )

        for attr, FieldClass, default_fn in [  # noqa:N806
            ("call", StrategyField, _default_call),
            ("catch", MorphingField, _default_catch),
        ]:
            if attr in namespace:
                val = namespace[attr]
                if not hasattr(val, "__get__"):
                    namespace[attr] = FieldClass(val)
            else:
                base_val = _find_mountable(attr, bases, {})
                if base_val is None:
                    namespace[attr] = FieldClass(default_fn)

        return super().__new__(mcs, name, bases, namespace, data)


@portlink(Meta)
class _Gcf1FunctorMeta(SstMeta):
    """Create Blueprint for Active Functorials"""

    def __new__(mcs, name, bases, namespace, data):
        _emit = _find_mountable("emit", bases, namespace) or _default_emit
        namespace["emit"] = _emit

        # call
        raw_call = namespace.get("call", _default_call)
        if not isinstance(raw_call, StrategyField):
            namespace["call"] = StrategyField(raw_call)

        # catch
        raw_catch = namespace.get("catch", _default_catch)
        if not isinstance(raw_catch, MorphingField):
            namespace["catch"] = MorphingField(raw_catch)

        # NEW: also normalize any other StrategyFields the user put directly in the body
        for _key, val in list(namespace.items()):
            if isinstance(val, type) and issubclass(
                val, (StrategyField, MorphingField)
            ):
                continue  # already a field
            # If someone put a bare function that looks like a strategy, we could wrap it here.
            # For now we trust @StrategyField in the class body.

        return super().__new__(mcs, name, bases, namespace, data)
