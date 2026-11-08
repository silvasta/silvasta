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

# WARNING: what the type checker shows:
# └╴󰌠  _spec.py  2
#   ├╴  Argument to function `field_names` is incorrect: Expected `DataClass`, found `type[Self@_absorb]`
#   │    info: type `type[Self@_absorb]` is not assignable to protocol `DataClass`
#   │    info: └── protocol member `__dataclass_fields__` is not defined on type `type[Self@_absorb]` ty (invalid-argument-type) [138, 56]
#   └╴  Argument to function `fields` is incorrect: Expected `DataclassInstance | type[DataclassInstance]`, found `DataClassSpec`
#        info: type `DataClassSpec` is not assignable to any element of the union `DataclassInstance | type[DataclassInstance]`
#        info: ├── type `DataClassSpec` is not assignable to protocol `DataclassInstance`
#        info: │   └── protocol member `__dataclass_fields__` is not defined on type `DataClassSpec`
#        info: └── ... omitted 1 union element without additional context ty (invalid-argument-type) [174, 37]


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


def pluck(
    data: MutableMapping[str, Any],
    names: Set[str],
    /,
    *,
    destroy: bool = True,
    prefix: str = "",
) -> dict[str, Any]:
    """Shallow extract (and destroy) Keys from Data if in Names"""

    _extract = data.pop if destroy else data.__getitem__
    _fieldset = KeySet(names, prefix=prefix)

    return {
        valid_key: _extract(raw_key)
        for raw_key in data.keys()
        if (valid_key := _fieldset(raw_key))
    }


def pluck_dataclass(
    data: MutableMapping[str, Any],
    cls: DataClass,
    *,
    destroy: bool,
) -> dict[str, Any]:
    return pluck(data, field_names(cls), destroy=destroy)


def field_names(cls: DataClass) -> set[str]:
    """Extract Field Names of DataClass Cls or Unit"""
    return {f.name for f in _dc.fields(class_or_instance=cls)}


class SpecMixin:
    """Collect shared utils for Specs"""

    if TYPE_CHECKING:
        __dataclass_fields__: ClassVar[dict[str, _dc.Field[Any]]]

    #  LINE: -- Maybe not only Spec Mixin? -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def evolve(self, **changes: Any) -> Self:
        """Return a new instance with updated fields."""
        return _dc.replace(self, **changes)

    @classmethod
    @cache
    # IDEA: make this KeySet (rename to FieldSet?)
    # - cached at first hit, provides easy check afterwards (forward __contains__?)
    def field_names(cls) -> frozenset[str]:
        """Cached set of dataclass field names."""
        return frozenset(f.name for f in _dc.fields(cls))

    #  LINE: -- Spec Features -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    @classmethod
    def _absorb(
        cls,
        kwargs: dict[str, Any],
        /,
        *,
        prefix: str = "",
        destroy: bool = True,
    ) -> Self:
        """Extract matching fields from Kwargs"""

        # AI_TASK: this looks quite good, refactor and replace with pluck above, dict->MutableMapping

        _pick = kwargs.pop if destroy else kwargs.__getitem__

        if not prefix:
            extracted = {
                k: _pick(k) for k in list(kwargs) if k in cls.field_names()
            }
        else:
            extracted = {
                stripped: _pick(k)
                for k in list(kwargs)
                if k.startswith(prefix)
                and (stripped := k.removeprefix(prefix)) in cls.field_names()
            }

        return cls(**extracted)

    @classmethod
    def _absorb(cls, kwargs: dict, /, *, destroy: bool = True) -> Self:
        # REMOVE: after everything extracted
        _pick = (lambda k: kwargs.pop(k)) if destroy else (lambda k: kwargs[k])
        return cls(**{n: _pick(n) for n in field_names(cls) if n in kwargs})

    @classmethod
    def _absorb(cls, kwargs) -> Self:
        # REMOVE: after everything extracted, probably just __doc__
        """Build Spec with input from kwargs (extracted and destroyed)"""
        return cls(
            **{
                field.name: kwargs.pop(field.name)
                for field in _dc.fields(class_or_instance=cls)
                if field.name in kwargs
            }
        )

    def extract[T](self, target_cls: type[T]) -> T:
        # AI_QUESTION: any benefits from this? otherwise drop
        """
        Shallow-extract fields belonging to `target_cls` from `self`.

        Safer and faster than `dataclasses.asdict()` because it doesn't deep-copy objects.
        """
        return target_cls(
            **{
                f.name: getattr(self, f.name)
                for f in _dc.fields(target_cls)  # ty:ignore
            }
        )

    @classmethod
    def from_specs(cls, *specs: DataClassSpec | None, **overrides: Any) -> Self:
        """Merge multiple partial specs shallowly into a composite spec."""
        # AI_TASK: this as SpecMixin.merge: use pluck and absorb and combine everything
        merged: dict[str, Any] = {}
        valid_fields = cls.field_names()
        for spec in specs:
            if spec is not None:
                for f in _dc.fields(spec):
                    if f.name in valid_fields:
                        merged[f.name] = getattr(spec, f.name)
        merged.update(overrides)
        return cls(**merged)


#  LINE: -- Implementations -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# AI: This is already a bit more than a pure data structure implementation...
# - where else could this be placed?
#   in event.dto.param makes no sense as it is first used there but other sections like forge.func have nothing to do with events
# - otherwise when it is just because of this class, than keep here, still somehow related enough
class ParamSpec(SpecMixin, DataClassSpec, kw_only=False):
    """Confirm Input and apply Defaults"""


# NOTE: ArgSpec in port.casting
