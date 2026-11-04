"""
Define the Shape of the Arg Casting and Spec Preparation Pipeline

-
"""

__all__: list[str] = [
    "ArgCasting",
    "BaseCaster",
    "CastInput",
    "DataClassSpec",
    "ArgSpec",
    # types
    "CastPlan",
    "TypeRegistry",
]

import dataclasses as _dc
import typing as _t
from collections.abc import Callable, MutableMapping
from functools import cache
from typing import Any, Self
from typing import Protocol as _Protocol

from .empty import VOID, MayBe

type CastPlan = dict[str, ArgCasting]
type TypeRegistry = dict[Any, ArgCasting]


class CastInput[Some](_t.TypedDict, total=False):
    """Configuration flags for ArgCasting."""

    default: Some | VOID


@_t.runtime_checkable
class ArgCasting[Some = _t.Any](_Protocol):
    """Cast, Coerce, Resolve and/or Validate Function Input."""

    def __call__(
        self, target: Any, /, *, default: MayBe[Some] = VOID
    ) -> Some: ...


#  LINE: -- 1. Multi-Field Spec Base (TypedDict -> Dataclass) -- -- - -- --


@_t.dataclass_transform(kw_only_default=True)
class DataClassSpec:
    """
    Unified Base for Input-Sanitizing Spec Dataclasses.

    Replaces EventDTO::ParamSpec, Functor::BaseParamSpec, and ArgSpecBase.
    """

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

    @classmethod
    @cache
    def field_names(cls) -> frozenset[str]:
        """Cached set of dataclass field names."""
        return frozenset(f.name for f in _dc.fields(cls))  # ty:ignore

    def evolve(self, **changes: Any) -> Self:
        """Return a new instance with updated fields."""
        return _dc.replace(self, **changes)  # ty:ignore

    @classmethod
    def absorb(
        cls,
        kwargs: MutableMapping[str, Any],
        /,
        *,
        prefix: str = "",
        cast: Callable[[type[Self], dict[str, Any]], Any] | None = None,
    ) -> Self:
        """
        Pop matching fields from `kwargs` (mutating it in-place) and instantiate `cls`.

        Supports optional prefix stripping (e.g., prefix='header_').
        """
        extracted = cls._pop_fields(kwargs, prefix=prefix)
        if cast is not None:
            cast(cls, extracted)
        return cls(**extracted)

    @classmethod
    def absorb_optional(
        cls,
        kwargs: MutableMapping[str, Any],
        /,
        *,
        prefix: str = "",
        defaults: dict[str, Any] | None = None,
    ) -> Self | None:
        """
        Pop matching fields from `kwargs`. Return `cls(...)` ONLY if at least

        one field was present in `kwargs`, otherwise return `None`.
        """
        extracted = cls._pop_fields(kwargs, prefix=prefix)
        if not extracted:
            return None
        if defaults:
            for k, v in defaults.items():
                if extracted.get(k) is None:
                    extracted[k] = v
        return cls(**extracted)

    @classmethod
    def _pop_fields(
        cls, kwargs: MutableMapping[str, Any], *, prefix: str = ""
    ) -> dict[str, Any]:
        names = cls.field_names()
        if not prefix:
            return {k: kwargs.pop(k) for k in list(kwargs) if k in names}

        return {
            stripped: kwargs.pop(k)
            for k in list(kwargs)
            if k.startswith(prefix)
            and (stripped := k.removeprefix(prefix)) in names
        }

    def extract[T](self, target_cls: type[T]) -> T:
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
        merged: dict[str, Any] = {}
        valid_fields = cls.field_names()
        for spec in specs:
            if spec is not None:
                for f in _dc.fields(spec):  # ty:ignore
                    if f.name in valid_fields:
                        merged[f.name] = getattr(spec, f.name)
        merged.update(overrides)
        return cls(**merged)


#  LINE: -- 2. Single-Value Target Spec & Caster Base -- -- - -- --


class ArgSpec[T](DataClassSpec, frozen=True, slots=True):
    """Base for single-target normalization and validation specs (like PathSpec)."""

    target: T

    def validate(self) -> T:
        """Ensure input specification and return validated target."""
        return self.target


class BaseCaster[ArgT, OutT]:
    """
    Reusable orchestration base for ArgCasting implementations.

    Handles `VOID` / `default` target resolution (`aim`) and delegates to `cast_target`.
    """

    input_types: _t.ClassVar[type | tuple[type, ...]] = object

    def __init__(self, **kwargs: Any) -> None:
        self.default: Any = kwargs.pop("default", VOID)
        self.kwargs: dict[str, Any] = kwargs

    def __call__(
        self, target: MayBe[ArgT] = VOID, /, *, default: MayBe[OutT] = VOID
    ) -> OutT:
        selected = self.aim(target, default)
        return self.cast_target(selected)

    def aim(
        self, target: MayBe[ArgT], default: MayBe[OutT] = VOID
    ) -> ArgT | OutT | VOID:
        """Select target from incoming value, signature default, or caster default."""
        if target is VOID:
            return self.default if default is VOID else default
        if isinstance(target, self.input_types):
            return target
        return VOID

    def cast_target(self, target: ArgT | OutT | VOID, /) -> OutT:
        raise NotImplementedError
