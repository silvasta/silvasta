"""
Define the Shape and Behaviour of the Solid Objects

- Collect ideas for Concepts and possible Bases

                                  DependencyLevel.sstcore.port[0.2]
"""

__all__: list[str] = [
    "SstEnumBlueprint",
    "SstEnumMeta",
    "is_sstenum",
    "BaseEnum",
    "is_baseenum",
    # common
    "EnumZero",
    "PolicyEnum",
    "EnumMachine",
    "EnumOption",
    "OptionRegister",  # CHECK:
    "MixinCatalog",
    # views
    "EnumView",
    "EnumRepr",
    "EnumStr",
    # types
    "EnumId",
    "EnumRelation",
]


import typing as _t

from .empty import VOID as _VOID
from .empty import MayBe as _MayBe
from .structures._enum import (
    EnumId,
    EnumRelation,
    EnumRepr,
    EnumStr,
    SstEnumMeta,
)


class SstEnumBlueprint(_t.Protocol):
    """Rough sketch of the SstEnumMeta..."""

    _walk_for_zero: bool = False
    _zero_indexed: bool = False

    def __prepare__(metacls, cls, bases, zero=False, walk=False, **kwargs):  # noqa:N805
        """Resolve WalkZero and start Member Count on Zero on Hit"""

    def __new__(
        metacls, cls, bases, classdict, /, zero=False, walk=False, **kwargs
    ):
        """Destroy walk/zero kwargs and attach values to new emun cls"""

    def membership(cls, target, /) -> EnumRelation:  # noqa:N805
        """Check if Target is Enum Member, the Class itself or unrelated"""

    def resolve(cls, identifier: EnumId, /, default=None) -> EnumRelation:  # noqa:N805
        """Map [int|str|EnumT] to BaseEnum derivative, default or Raise"""


def _test(enum_type: SstEnumMeta) -> SstEnumBlueprint:
    """Show basic divergence/convergence..."""
    return enum_type  # TODO: find like a proper test


def is_sstenum(target: _t.Any, /) -> _t.TypeGuard[SstEnumBlueprint]:
    """Is the Target an EnumCls using SstEnumMeta?"""
    return isinstance(target, SstEnumMeta)


def is_baseenum(target: _t.Any, /) -> _t.TypeGuard[BaseEnum]:
    """Is the Target a Member of some BaseEnum?"""
    return isinstance(target, BaseEnum)


class EnumView(EnumStr, EnumRepr):
    """Global Default"""


class BaseEnum(EnumView, metaclass=SstEnumMeta):
    """Provide Base with Simple View and Modified Access"""


class EnumZero(BaseEnum, zero=True):
    """Index based Enum - propagate permanently to SubClasses with walk=True"""


#  LINE: -- frequently used -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PolicyEnum(EnumZero, walk=True):
    """Task and Rule Toggle"""

    def __bool__(self):  # CHECK: maybe for option? or for policy?
        """Default Policy mapped to Index 0"""
        return self.value == 0


class EnumMachine(BaseEnum):  # TODO: sketch StubMachine(Machine)
    """Task Executor"""


#  LINE: -- boundaries unclear... -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class EnumMode(BaseEnum):  # CHECK: same as Option?
    """Task Toggle"""


class EnumOption(EnumZero):
    """Multiple Selections - Always 1 default (on zero)"""


class PrintOption(EnumZero, walk=True):
    """(Randomly) toggle views until it looks nice"""


class OptionRegister(EnumZero, walk=True):  # REMOVE: when Fields settled
    """Provide Container to register Options for each Member"""

    _registry: dict[int, _t.Any]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry: dict[int, _t.Any] = {}

    @classmethod
    def register(cls, mapping: dict[_t.Self, _t.Any]) -> None:
        """Update the internal storage with Options for Member"""
        cls._registry.update(
            {enum.value: option for enum, option in mapping.items()}
        )

    def get(self, fallback: _MayBe[_t.Any] = _VOID):
        """Get Option that is registered for current Member"""
        try:
            return self._registry[self.value]
        except KeyError as err:
            if fallback is not _VOID:
                return fallback
            raise RuntimeError(f"Unregistered {type(self).__name__}") from err


class EnumCatalog(BaseEnum):
    """Foolproof Selection"""

    @property
    def topic(self) -> str:  # IDEA: class-def-arg? (maybe enum cls dto)
        return "SstCatalog"

    @property
    def category(self) -> str:
        return type(self).__name__.lower()

    def __str__(self) -> str:  # CHECK:
        return f"{type(self).__name__}{self.topic}[{self.name}]"


class MixinCatalog(EnumCatalog):
    """Select without Surprise"""

    @property
    def mixin(self) -> type:
        raise NotImplementedError


#  LINE: -- StateMachine -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class StateGraph(EnumView):
    """Static Decision Tool"""


class Transition(EnumView):
    """Dynamic Decision Tool"""
