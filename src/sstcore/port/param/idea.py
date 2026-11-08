"""
Define the Base of the DataClass Tribes

- maybe merge with port._data or expose logic together

"""

import dataclasses as _dc
from collections.abc import Mapping
from functools import cache
from typing import Any, Self, dataclass_transform


@dataclass_transform(kw_only_default=True)
class SpecDataClass:
    """Provide Base for Input-Sanitizing Spec Dataclasses"""

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


@dataclass_transform(kw_only_default=True)  # CHECK: place or not?
class SpecMixin:
    """Collect shared utils for Specs"""

    # IMPORTANT:
    @classmethod
    def absorb(
        cls,
        data: Mapping,
        /,
        *,
        destroy: bool = True,
        # AI: the following may be considered
        # prefix: str = "",
        # defaults: dict[str, Any] | None = None,
    ) -> Self:
        """Prepare instance from Mapping"""
        raise NotImplementedError

    # IDEA:
    @classmethod
    @cache
    def fields(cls) -> frozenset[str]:
        """Cached set of dataclass field names."""
        # WARNING:
        # │ ├╴  Argument to function `fields` is incorrect: Expected `DataclassInstance | type[DataclassInstance]`, found `type[Self@fields]`
        # │ │
        # │ │    info: type `type[Self@fields]` is not assignable to any element of the union `DataclassInstance | type[DataclassInstance]`
        # │ │    info: ├── type `type[Self@fields]` is not assignable to protocol `DataclassInstance`
        # │ │    info: │   └── protocol member `__dataclass_fields__` is not defined on type `type[Self@fields]`
        # │ │    info: └── type `SpecMixin` is not assignable to protocol `DataclassInstance`
        # │ │    info:     └── protocol member `__dataclass_fields__` is not defined on type `SpecMixin` ty (invalid-argument-type) [54, 53]
        return frozenset(f.name for f in _dc.fields(cls))

    # IDEA:
    def evolve(self, **changes: Any) -> Self:
        """Return a new instance with updated fields."""
        return _dc.replace(self, **changes)

    # TODO: others


class ArgSpec(SpecMixin, SpecDataClass, frozen=True, slots=True): ...


class ParamSpec(SpecMixin, SpecDataClass, kw_only=False): ...


# AI: unsure about EventDTO and BaseEventDTO
