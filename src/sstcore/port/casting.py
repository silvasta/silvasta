"""
Define the Shape of the Arg Casting Pipeline

- Mount on functions and cast args

                              DependencyLevel.sstcore.port.empty[1]
"""

__all__: list[str] = [
    "ArgCasting",
    "CastInput",
    # types
    "CastPlan",
    "TypeRegistry",
]

import dataclasses as _dc
import typing as _t
from collections.abc import Callable
from typing import Any
from typing import Protocol as _Protocol

from .empty import VOID, MayBe
from .input import TEST as TEST

type CastPlan = dict[str, ArgCasting]
type TypeRegistry[T: type] = dict[T, ArgCasting]


class CastInput[Some](_t.TypedDict, total=False):
    """Configuration flags for ArgCasting"""

    default: Some | VOID


@_t.runtime_checkable
class ArgCasting[Some = _t.Any](_Protocol):
    """Cast, Coerce, Resolve and/or Validate Function Input"""

    def __call__(self, target, /, *, default: MayBe[Some] = VOID) -> Some:
        """Cast, Coerce, Resolve and or Validate the Function Input"""


TYPE_REGISTRY: TypeRegistry[Any] = {}
ANNOTATED_BINDERS: dict[
    Any, Callable[[tuple[Any, ...]], ArgCasting | None]
] = {}


def register_caster(
    target: Any, caster: ArgCasting, *, replace: bool = False
) -> None:
    if (
        not replace
        and target in TYPE_REGISTRY
        and TYPE_REGISTRY[target] is not caster
    ):
        raise TypeError(f"caster already registered for {target!r}")
    TYPE_REGISTRY[target] = caster


def register_annotated(
    origin: Any,
    binder: Callable[[tuple[Any, ...]], ArgCasting | None],
    *,
    replace: bool = False,
) -> None:
    if not replace and origin in ANNOTATED_BINDERS:
        raise TypeError(f"binder already registered for {origin!r}")
    ANNOTATED_BINDERS[origin] = binder


#  LINE: -- Spec -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@_t.dataclass_transform(kw_only_default=True)
class SpecBaseDataClass:
    """Setup Base for Input sanitizing DataClasses"""

    def __init_subclass__(cls, kw_only: bool = True, **kwargs):
        super().__init_subclass__(**kwargs)
        _dc.dataclass(kw_only=kw_only, **kwargs)(cls)


class SpecBase(SpecBaseDataClass):
    """Единая основа для всех dataclasses, работающих с входными данными."""

    @classmethod
    def field_names(cls) -> frozenset[str]:
        return frozenset(f.name for f in _dc.fields(cls))

    @classmethod
    def absorb(cls, kwargs: dict, /, *, destroy: bool = True) -> _t.Self:
        # NEXT: compare with other specs
        """Выбрать известные поля из kwargs; разрушительный режим по умолчанию."""
        pick = (lambda k: kwargs.pop(k)) if destroy else (lambda k: kwargs[k])
        return cls(**{n: pick(n) for n in cls.field_names() if n in kwargs})

    def evolve(self, **changes) -> _t.Self:
        return _dc.replace(self, **changes)


class ArgSpec[T](SpecBase):
    """Уровень для зарегистрированных кастеров: базовый тип + normalize/validate."""

    target: T

    @classmethod
    def ok(cls, target: MayBe[T] = VOID, /, **kwargs) -> T:
        """Normalize and Validate Input and provide resolved Target"""
        return cls.normalize(target, **kwargs).validate()

    @classmethod
    def normalize(cls, target=VOID, /, **kwargs) -> _t.Self:
        raise NotImplementedError(target, kwargs)

    def validate(self) -> T:
        """Ensure Specification and provide resolved Target"""
        raise NotImplementedError
