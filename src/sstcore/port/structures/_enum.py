"""
Govern the Shape and Structure of the Strict and Reliable Container

                     DependencyLevel.sstcore.port.structures[0.1.0]
"""

__all__: list[str] = [
    "SstEnumMeta",
    # types and helper
    "EnumId",
    "EnumRelation",
    "WalkZero",
    "from_zero",
    # view
    "EnumStr",
    "EnumRepr",
    # more views
    "EnumStr1",
    "EnumStr2",
    "EnumRepr1",
]


from enum import Enum, EnumDict, EnumMeta
from typing import Any, NamedTuple, Self

from .._error import SstError
from ._enumfield import EnumFieldMap
from ._gate import GateRaiser

type EnumId[EnumT: Enum] = EnumT | str | int

type EnumRelation[T: Enum] = tuple[type[T], T] | tuple[type[T]] | tuple[()]

type EnumType = type[Enum] | SstEnumMeta


class SstEnumMeta(EnumMeta):
    """Tune Enum Meta with some Features"""

    _walk_for_zero: bool = False
    _zero_indexed: bool = False
    _enum_fields_: EnumFieldMap

    @classmethod
    def __prepare__(
        metacls,  # noqa:N804
        cls: str,
        bases: tuple[type, ...],
        zero=False,
        walk=False,
        **kwds,
    ) -> EnumDict:
        _ = metacls

        enum_dict: EnumDict = super().__prepare__(cls, bases, **kwds)

        if WalkZero.resolve(walk, zero, bases).zero:
            enum_dict["_generate_next_value_"] = staticmethod(from_zero)

        return enum_dict

    def __new__(
        metacls,
        cls: str,
        bases: tuple[type, ...],
        classdict: EnumDict,
        *,
        zero=False,
        walk=False,
        **kwds: Any,
    ):
        """Destroy all custom kwargs and attach Zero"""

        resolved: WalkZero = WalkZero.resolve(walk, zero, bases)

        new_enum_cls = super().__new__(metacls, cls, bases, classdict, **kwds)
        new_enum_cls._zero_indexed = resolved.zero
        new_enum_cls._walk_for_zero = resolved.walk
        if issubclass(new_enum_cls, Enum):
            new_enum_cls._enum_fields_ = EnumFieldMap(new_enum_cls)

        return new_enum_cls

    def membership(cls, target, /) -> EnumRelation:
        """Check with EnumCls if Target is (Sub-)Class or Member"""
        if isinstance(target, cls):
            return (type(target), target)
        if isinstance(target, EnumMeta) and issubclass(target, cls):
            return (target,)
        return ()

    @classmethod
    def classify(metacls, target: Any, /) -> EnumRelation:  # noqa: N804
        """Check with SstEnumMeta if Target is (Sub-)Class or Member"""
        if isinstance(target, metacls):
            return (target,)
        if isinstance(type(target), metacls) and isinstance(target, Enum):
            return (type(target), target)
        return ()

    def resolve(cls, identifier: EnumId, /, default=None):
        try:
            match identifier:
                case cls():
                    return identifier
                case int() as index:
                    return cls(index)
                case str() as name:
                    for member_name, member in cls._member_map_.items():
                        if name.lower() == member_name.lower():
                            return member
                    raise GateRaiser.enum_member(cls.__name__, identifier)
                case _:
                    raise GateRaiser.enum_type("Resolve", cls, identifier)
        except ValueError, KeyError, TypeError:
            if default is None:
                raise
        return default

    def validate_fields(cls, *, strict: bool = False) -> None:
        """Validate all EnumField descriptors attached to this Enum."""
        cls._enum_fields_.validate(strict=strict)

    def fields_ready(cls) -> bool:
        """Check whether all attached EnumFields have been hydrated."""
        return cls._enum_fields_.is_ready

    @staticmethod
    def validate_all_registered(*, strict: bool = False) -> None:
        """Single test-suite hook to hydrate & validate every EnumField"""
        EnumFieldMap.validate_all(strict=strict)


class WalkZero(NamedTuple):
    walk: bool
    zero: bool

    @classmethod
    def resolve(cls, walk: bool, zero: bool, bases: tuple[type, ...]) -> Self:
        """Resolve inherited walk and zero flags from kwargs and bases"""
        walked_walk: bool = walk or any(
            getattr(base, "_walk_for_zero", False) for base in bases
        )
        zero_or_walked_zero: bool = zero or (
            walk
            and any(getattr(base, "_zero_indexed", False) for base in bases)
        )
        return cls(walked_walk, zero_or_walked_zero)


def from_zero(name, start, count, last_values):
    """Start from Index Zero"""
    _, _, _ = name, start, last_values
    return count


class EnumError(SstError, TypeError):
    """Temporary Resolve the SstEnumMeta blinding"""

    def __init__(
        self, member_or_cls: Enum | type[Enum], /, reason="", *args, **kwargs
    ) -> None:
        """Forward Args to Exception"""
        reason: str = reason or "Failed"
        match SstEnumMeta.classify(member_or_cls):
            case ():
                who = f"Unknown: {member_or_cls=}"
            case (enum_cls,):
                self.enum: SstEnumMeta = enum_cls
                who = f"BaseEnum: {enum_cls}"
            case (enum_cls, member):
                self.enum: SstEnumMeta = enum_cls
                self.member: Enum = member
                who = f"BaseEnum: {enum_cls=}, {member=}"
        super().__init__(f"{who} | {reason=}", *args, **kwargs)


#  LINE: -- views -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class EnumStr1(Enum):
    def __str__(self) -> str:
        return f"{self.name.capitalize()}"


class EnumStr2(Enum):
    def __str__(self):
        return self.name


class EnumRepr1(Enum):
    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.value}]::{self}"


EnumStr = EnumStr2
EnumRepr = EnumRepr1


if __name__ == "__main__":
    from dataclasses import dataclass
    from enum import Enum
    from typing import ClassVar, Protocol

    class HasRouting(Protocol):
        prefix: str
        routing_key: str

    @dataclass(frozen=True)
    class RabbitDTO:
        prefix: str
        routing_key: str
        exchange: str

    class RootEnum(Enum):
        config: ClassVar[object]  # Generic or broad baseline

        def __init_subclass__(cls, config: object, **kwargs):
            super().__init_subclass__(**kwargs)
            cls.config = config

    class QueueEnum(
        RootEnum, config=RabbitDTO("app.", "orders.#", "amq.direct")
    ):
        config: ClassVar[HasRouting]

        ORDERS = "orders"

    print(QueueEnum.config.routing_key)
