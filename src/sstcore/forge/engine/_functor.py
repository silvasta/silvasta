"""
Shape the Blueprint for Functors acting in different Spaces

FunctorMeta
  - ...

"""

__all__: list[str] = [
    "FunctorMeta",
    "FunctorMetaData",
]

from typing import Any

from ...brick.field import MethodFieldEngine
from ...brick.none import sentinel
from ...port.link import portlink
from ...port.shape import Meta, MetaData
from ._meta_base import SstMeta, SstMetaData

_MISSING = sentinel("MISSING")


@portlink(MetaData)
class FunctorMetaData(SstMetaData):
    """# NOTE: so far nothing interesting to add..."""


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

        sync_inherited_strategy_fields(namespace, bases)
        return super().__new__(mcs, name, bases, namespace, data)


def sync_inherited_strategy_fields(
    namespace: dict[str, Any],
    bases: tuple[type, ...],
    /,
) -> None:
    """
    Ensure Functor Strategies

    1. Discover all `MethodFieldEngine` descriptors in the MRO of `bases`.
    2. If a subclass overrode the slot with a plain callable `def fn(self):`,
       wrap it in the parent's `MethodFieldEngine` type (`StrategyField` / `MorphingField`).
    3. If the subclass did not override it, clone the descriptor so class-level
       `.switch()` / `.morph()` mutations on the subclass do not bleed into the base class.
    """
    inherited_engines: dict[str, MethodFieldEngine] = {}

    for base in bases:
        for parent in base.__mro__:
            if parent is object:
                continue
            for attr_name, attr_val in parent.__dict__.items():
                if attr_name not in inherited_engines and isinstance(
                    attr_val, MethodFieldEngine
                ):
                    inherited_engines[attr_name] = attr_val

    for field_name, parent_engine in inherited_engines.items():
        existing = namespace.get(field_name, _MISSING)

        if isinstance(existing, MethodFieldEngine):
            continue

        if callable(existing):
            namespace[field_name] = type(parent_engine)(
                existing, bind_to_self=True
            )
            continue

        if existing is _MISSING and parent_engine.target_func is not None:
            namespace[field_name] = type(parent_engine)(
                parent_engine.target_func,
                bind_to_self=parent_engine.bind_to_self,
            )
