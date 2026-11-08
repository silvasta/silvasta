"""
Combine all exsiting ideas for dataclass bases in one file

-
"""

# AI: this was distributed all around the library before, and should be again
# - the base will stay in the port, mainly to provide port.event.dto or some ParamSpecs
# - argcast related stuff will move to port.casting or brick.call._{arg}cast
# - functor input/spec should go back to functor similar for any other spec/dto pair
#   - some spec/dto pairs may stay in the port, depending how early they are needed

import dataclasses as _dc
from collections.abc import Callable, MutableMapping
from dataclasses import dataclass, fields
from functools import cache
from typing import Any, Self, TypedDict, Unpack, dataclass_transform

from src.sstcore.port.color import ColorArg
from src.sstcore.port.empty import VOID, MayBe
from src.sstcore.port.event.dto import MergedDtoInputs
from sstcore.port.color import Color
from sstcore.port.event.dto import BaseEventDTO

from ...port.functorial import Catch, ErrorPolicy
from .._types import _Boxes
from .argcast import ArgCast
from .cast import apply_mapping

#  LINE: -- V1 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass_transform(kw_only_default=True)
class SpecBase:
    def __init_subclass__(cls, kw_only: bool = True, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        dataclass(kw_only=kw_only, **kwargs)(cls)

    @classmethod
    def pack(cls, kwargs: dict[str, Any]) -> dict[str, Any]:
        return kwargs

    @classmethod
    def absorb(cls, kwargs: dict[str, Any], *, cast: bool = False) -> Self:
        packed = cls.pack(kwargs)
        if cast:  # CHECK: needed/desired?
            apply_mapping(ArgCast.walk(cls), packed)
        return cls(**pluck(packed, cls, consume=True))


def pluck(data: dict[str, Any], cls: type, *, consume: bool) -> dict[str, Any]:
    names: set[str] = {field.name for field in fields(cls)}
    if consume:
        return {key: data.pop(key) for key in list(data) if key in names}
    return {key: data[key] for key in names & data.keys()}


#  LINE: -- V2 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass_transform(kw_only_default=True)
class DataClassBase:
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


class DataClassSpec(DataClassBase):
    @classmethod
    @cache
    def field_names(cls) -> frozenset[str]:
        """Cached set of dataclass field names."""
        return frozenset(f.name for f in _dc.fields(cls))

    def evolve(self, **changes: Any) -> Self:
        """Return a new instance with updated fields."""
        return _dc.replace(self, **changes)

    @classmethod
    def _absorb(cls, kwargs: dict, /, *, destroy: bool = True) -> Self:
        # NEXT: compare with other absorb
        # IMPORTANT: one is needed to just build from spec
        _pick = (lambda k: kwargs.pop(k)) if destroy else (lambda k: kwargs[k])
        return cls(**{n: _pick(n) for n in cls.field_names() if n in kwargs})

    @classmethod
    def _absorb(
        cls,
        kwargs: MutableMapping[str, Any],
        /,
        *,
        prefix: str = "",
        # CHECK: why is here some very strange callable?
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
        if not prefix:
            return {
                k: kwargs.pop(k) for k in list(kwargs) if k in cls.field_names()
            }
        return {
            stripped: kwargs.pop(k)
            for k in list(kwargs)
            if k.startswith(prefix)
            and (stripped := k.removeprefix(prefix)) in cls.field_names()
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
                for f in _dc.fields(spec):
                    if f.name in valid_fields:
                        merged[f.name] = getattr(spec, f.name)
        merged.update(overrides)
        return cls(**merged)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _ArgSpec[T](DataClassSpec, frozen=True, slots=True):
    # WARNING:
    # ├╴  Frozen dataclass cannot inherit from non-frozen dataclass: Subclass `_ArgSpec` is frozen but base class `DataClassSpec` is not
    """Base for single-target normalization and validation specs (like PathSpec)."""

    target: T

    def validate(self) -> T:
        """Ensure input specification and return validated target."""
        return self.target


class _ArgSpec[T](DataClassSpec):
    target: T

    @classmethod
    def ok(cls, target: MayBe[T] = VOID, /, **kwargs) -> T:
        """Normalize and Validate Input and provide resolved Target"""
        return cls.normalize(target, **kwargs).validate()

    @classmethod
    def normalize(cls, target=VOID, /, **kwargs) -> Self:
        raise NotImplementedError(target, kwargs)

    def validate(self) -> T:
        """Ensure Specification and provide resolved Target"""
        raise NotImplementedError


class FrameSpec(DataClassSpec):
    topic: str | None = ""
    topic_color: Color = Color.WHITE
    box: _Boxes = _Boxes.CORNER


class HeaderSpec(DataClassSpec):
    title: str | None = None
    frame: FrameSpec = _dc.field(default_factory=FrameSpec)


class EventDTO(BaseEventDTO, name="ctor"):
    @classmethod
    def create(cls, *args, **kwargs) -> Self:
        target_cls: type[Self] = cls._registry.get(cls.name, cls)
        sanitized: dict[str, Any] = target_cls._sanitize_kwargs(**kwargs)
        # Optional: ArgCast.cast_dict(target_cls, sanitized)
        #
        return target_cls(*args, **sanitized)

    @classmethod  # LATER: where to apply @castarg?
    def _sanitize_kwargs(
        cls, **kwargs: Unpack[MergedDtoInputs]
    ) -> dict[str, Any]:
        """Pack nested ParamSpec and resolve Annotated types"""
        return sanitize_specs(
            fields=frozenset(
                {field.name for field in _dc.fields(class_or_instance=cls)}
            ),
            **kwargs,
        )


def sanitize_specs(fields: frozenset[str], **kwargs: Any) -> dict[str, Any]:
    spec: dict[str, Any] = dict(kwargs)

    if "frame" in fields and "frame" not in spec:
        if frame := FrameSpec.absorb_optional(spec):
            spec["frame"] = frame

    if "header" in fields and "header" not in spec:
        main_frame: FrameSpec | None = spec.get("frame")
        default_box = main_frame.box if main_frame else _Boxes.CORNER

        header_frame = FrameSpec.absorb_optional(
            spec, prefix="header_", defaults={"box": default_box}
        )
        title: str | None = spec.pop("title", None)

        if title is not None or header_frame is not None:
            spec["header"] = HeaderSpec(
                title=title,
                frame=header_frame or FrameSpec(box=default_box),
            )

    return spec


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

# AI: here the input parsing DTOs with corresponding TypedDict


@dataclass_transform(kw_only_default=True)
class ParamSpec:  # TODO: compV
    """Base for dataclasses that parse Param Input (FrameSpec, HeaderSpec,..)"""

    def __init_subclass__(cls, kw_only: bool = True, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        _dc.dataclass(kw_only=kw_only, **kwargs)(cls)


class FrameSpec(ParamSpec):
    """The Box around the Renderable - supplies Content and Frame"""

    topic: str | None = ""
    topic_color: Color = Color.WHITE
    box: _Boxes = _Boxes.CORNER


class FrameTopicInput(TypedDict, total=False):
    topic: str
    topic_color: ColorArg


class FrameInput(FrameTopicInput, total=False):
    """Define the Border of one Header or Main Content"""

    box: _Boxes


class _HeaderSpec(ParamSpec):
    title: str | None = None
    frame: FrameSpec = _dc.field(default_factory=FrameSpec)


class HeaderBaseInput(TypedDict, total=False):
    title: str


class HeaderFrameInput(TypedDict, total=False):
    header_topic: str
    header_topic_color: ColorArg
    header_box: _Boxes | None  # None = Same as Main Content


class HeaderInput(HeaderBaseInput, HeaderFrameInput, total=False):
    """Combine Header with Frame Args"""


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass_transform(kw_only_default=True)
class BaseParamSpec:  # TODO: compare with EventDTO::ParamSpec, find global base
    """Setup Base for Input sanitizing DataClasses"""

    def __init_subclass__(cls, kw_only: bool = True, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        dataclass(kw_only=kw_only, **kwargs)(cls)


class BaseInput(TypedDict, total=False): ...


class DataClassSpec(BaseParamSpec):
    """Define Defaults for Input and Sanitize"""

    @classmethod  # IDEA: combine with @castarg?
    def absorb(cls, kwargs) -> Self:
        """Build Spec with input from kwargs (extracted and destroyed)"""
        return cls(
            **{
                field.name: kwargs.pop(field.name)
                for field in fields(class_or_instance=cls)
                if field.name in kwargs
            }
        )


class FunctorInput[**A, R](TypedDict, total=False):
    call: Callable[A, R]
    name: str


class FunctorSpec[**A, R](DataClassSpec):
    call: Callable[A, R] | None = None
    name: str = ""


class SafeFunctorInput[**A, R](FunctorInput, total=False):
    catch: Catch[A, R]
    policy: ErrorPolicy
    exit_code: int


class SafeFunctorSpec[**A, R](DataClassSpec):
    catch: Catch[A, R] | None = None
    policy: ErrorPolicy | None = None
    exit_code: int | None = None
