"""
Spec

                     DependencyLevel.sstcore.port.structures[0.1.1]
"""

__all__: list[str] = [
    "DataClass",
    "DataClassSpec",
    "ParamSpec",
    # TODO:
]


import dataclasses as _dc
import typing as _t
from collections.abc import MutableMapping, Set
from functools import cache
from typing import TYPE_CHECKING, Any, ClassVar, Self

from ._frozen import KeySet


class DataClass(_t.Protocol):
    """Define the minimal Shape for typing a DataClass"""

    __dataclass_fields__: _t.ClassVar[dict[str, Any]]


@_t.dataclass_transform(kw_only_default=True)
class DataClassSpec:
    """Base for Input-Sanitizing dataclass Specs"""

    def __init_subclass__(
        cls,
        *,
        kw_only: bool = True,
        frozen: bool = False,
        slots: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        _dc.dataclass(kw_only=kw_only, frozen=frozen, slots=slots)(cls)


class SpecMixin:
    """Collect shared utils for Specs"""

    if TYPE_CHECKING:
        __dataclass_fields__: ClassVar[dict[str, _dc.Field[Any]]]

    #  LINE: -- Maybe not only Spec Mixin? -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def evolve(self, **changes: Any) -> Self:
        """Provide new instance with updated fields"""
        return _dc.replace(self, **changes)

    @classmethod
    @cache
    def field_names(cls) -> KeySet:
        """Cached set of dataclass field names."""
        return KeySet(field_names(cls))  # ty:ignore FIX: cls fails, why?

    @classmethod
    def absorb(
        cls,
        kwargs: MutableMapping[str, Any],
        /,
        *,
        prefix: str = "",
        destroy: bool = True,
    ) -> Self:
        """Extract matching fields from kwargs to create new instance"""
        return cls(
            **pluck(kwargs, cls.field_names(), destroy=destroy, prefix=prefix)
        )

    @classmethod
    def merge(cls, *specs: DataClass, **overrides) -> Self:
        """Merge multiple partial specs shallowly into a composite spec."""
        merged: dict[str, Any] = {
            field.name: getattr(spec, field.name)
            for spec in specs
            # AI: is this possible shorter? like with the KeySet.__call__?
            for field in _dc.fields(class_or_instance=spec)
            if field.name in cls.field_names()
        }
        # REMOVE: when version above fine
        # for spec in specs:
        #     if spec is not None:
        #         for f in _dc.fields(class_or_instance=spec):
        #             if f.name in cls.field_names():
        #                 merged[f.name] = getattr(spec, f.name)
        merged.update(overrides)
        return cls(**merged)


def pluck(  # AI: merge this directly into SpecMixin.absorb? or ever usable standalone?
    data: MutableMapping[str, Any],
    names: Set[str],
    /,
    *,
    destroy: bool = True,
    prefix: str = "",
) -> dict[str, Any]:
    """Shallow extract (and destroy) Keys from Data if in Names"""

    _extract = data.pop if destroy else data.__getitem__
    _names = KeySet(names, prefix=prefix)

    return {
        valid_key: _extract(raw_key)
        for raw_key in data.keys()
        if (valid_key := _names(raw_key))
    }


def field_names(cls: DataClass) -> set[str]:
    """Extract Field Names of DataClass Cls or Unit"""
    return {f.name for f in _dc.fields(class_or_instance=cls)}


#  LINE: -- Implementations -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ParamSpec(SpecMixin, DataClassSpec, kw_only=False):
    """Confirm Input and apply Defaults"""


# NOTE: ArgSpec is in port.casting
