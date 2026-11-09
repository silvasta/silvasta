"""
Draw the Shape of the Core Data Structures

                                  DependencyLevel.sstcore.port[0.1]
"""

__all__: list[str] = [
    "NormSet",
    "KeySet",
    "FieldSet",
    "DunderSet",
    "frozendict",
    "HashedTuple",
    "ParamSnap",
    # dataclass
    "DataClass",
    "CachedDataclassMeta",
    "create_field_resolver",
    "SpecBase",
    "DataClassSpec",
    "ParamSpec",
    "ArgSpec",
    # enum
    "SstEnumMeta",
    "EnumId",
    "EnumStr",
    "EnumRepr",
    "EnumRelation",
    # cls namespaces
    "PresetMeta",
    "LockedClsMeta",
]

from typing import Any as _Any

from .._types import Types as _T  # noqa: N814
from .._types import _LockedClsMeta as LockedClsMeta
from ._dataclass import (
    ArgSpec,
    CachedDataclassMeta,
    DataClass,
    DataClassSpec,
    ParamSpec,
    SpecBase,
    create_field_resolver,
)
from ._enum import EnumId, EnumRelation, EnumRepr, EnumStr, SstEnumMeta
from ._map import frozendict
from ._set import DunderSet, FieldSet, KeySet, NormSet
from ._tuple import HashedTuple, ParamSnap


class PresetMeta(LockedClsMeta):
    def __new__(mcls, name: str, bases: _T.Bases, namespace: _T.NameSpace):
        """
        Convert Mutable Structures and lock everything possible

        - set  -> frozenset
        - list -> tuple
        - dict -> frozendict
        """
        frozen_items: dict[str, _Any] = {
            key: HashedTuple.hash(value)
            for key, value in namespace.items()
            if not key.startswith("_")  # LATER: by toggle? (AttrFilter)
        }
        namespace.update(frozen_items)
        namespace.setdefault("__slots__", ())
        return super().__new__(mcls, name, bases, namespace)
