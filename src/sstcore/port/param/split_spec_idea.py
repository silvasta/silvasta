import dataclasses as _dc
from functools import cache
from typing import Any, Self, dataclass_transform

from sstcore.port.color import Color
from sstcore.port.empty import VOID


@dataclass_transform(kw_only_default=True)
class SpecMixin:
    """Pure utility mixin for dictionary absorption"""

    @classmethod
    @cache
    def field_names(cls) -> frozenset[str]:
        return frozenset(f.name for f in _dc.fields(cls))

    @classmethod
    def absorb(
        cls,
        kwargs: dict[str, Any],
        /,
        *,
        prefix: str = "",
        consume: bool = True,
    ) -> Self:
        """Extract matching fields from Kwargs"""

        _pick = (lambda k: kwargs.pop(k)) if consume else (lambda k: kwargs[k])

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

    def evolve(self, **changes: Any) -> Self:
        return _dc.replace(self, **changes)


#  LINE: -- Tribe 1 - Pure DTOs -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@_dc.dataclass(kw_only=True, slots=True)
class ParamSpec(SpecMixin):
    """Base for pure input DataClasses (FrameSpec, HeaderSpec)."""


# Usage:
@_dc.dataclass(kw_only=True, slots=True)
class FrameSpec(ParamSpec):
    topic: str | None = ""
    topic_color: Color = Color.WHITE


#  LINE: -- Tribe 2 - ArgSpecs -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@_dc.dataclass(kw_only=True, frozen=True, slots=True)
class ArgSpec[T](SpecMixin):
    """Base for single-target validation specs."""

    target: T

    @classmethod
    # WARN: this shouldn't overwrite the class.__call__
    def __call__(cls, target: Any = VOID, /, *, default: Any = VOID) -> T:
        """Allow ArgCast to use this class directly as a caster plugin"""
        return cls.ok(target)

    @classmethod
    def ok(cls, target: Any = VOID, /, **kwargs) -> T:
        return cls.normalize(target, **kwargs).validate()

    @classmethod
    def normalize(cls, target=VOID, /, **kwargs) -> Self:
        raise NotImplementedError(target, kwargs)

    def validate(self) -> T:
        return self.target


#  LINE: -- Tribe 3 - ArgSpecs -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@_dc.dataclass(kw_only=True)
class EventDTO(SpecMixin):
    """Base for mission-driven Event orchestrators."""

    @classmethod
    def create(cls, *args, **kwargs) -> Self:
        # 1. Use the Mixin to sanitize/pluck specific kwargs
        # 2. Execute Event-specific setup logic
        # 3. Instantiate
        sanitized = cls.absorb(kwargs, consume=False)
        return cls(*args, **sanitized)
