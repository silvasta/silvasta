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
from ...port.empty import VOID, MayBe
from ...port.link import portlink
from ...port.shape import Meta, MetaData
from ._meta_base import SstMeta, SstMetaData


@portlink(Meta)
class FunctorMeta(SstMeta):
    """Create the Skeleton for dynamic and flexibel Functorials"""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: MayBe[FunctorMetaData] = VOID,
        # AI: opening the Cls paramspace here is the least worse solution
        # - still, on the base Meta this is not desired!
    ):
        if data is VOID:
            data: FunctorMetaData = _inherit_data(bases, FunctorMetaData)
        sync_inherited_strategy_fields(namespace, bases)
        return super().__new__(mcs, name, bases, namespace, data)


@portlink(MetaData)
class FunctorMetaData(SstMetaData):
    """Likely that this will be extended soon.."""


def _inherit_data[Data: SstMetaData](
    bases: tuple[type, ...], factory: type[Data]
) -> Data:  # MOVE: maybe useful for other? Don't mount in Base!!
    for base in bases:
        found: MayBe[Data] = getattr(base, "_data", VOID)
        if isinstance(found, factory):  # CHECK: what is minimum? factory fine?
            return found
        # LATER: check what is if found is other SstMetaData, other or even None
    return factory()


def sync_inherited_strategy_fields(
    namespace: dict[str, Any],
    bases: tuple[type, ...],
    /,
) -> None:
    """
    Ensure all Strategy- and MorphingFields are mounted on Functor

    - Discover all MethodField Descriptors in bases by walking the MRO
    - Wrap with plain callable overridden slots into the corresponding Fields
    - Otherwise Clone Descriptors to avoid that mutations bleed into the Base
      - switch() and morph() should not change class-level attributes

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
        existing = namespace.get(field_name, VOID)

        if isinstance(existing, MethodFieldEngine):
            continue

        if callable(existing):  # WARN: for type mounted on cls, callable?
            namespace[field_name] = type(parent_engine)(
                existing, bind_to_self=True
            )
            continue

        if existing is VOID and parent_engine.target_func is not None:
            namespace[field_name] = type(parent_engine)(
                parent_engine.target_func,
                bind_to_self=parent_engine.bind_to_self,
            )
