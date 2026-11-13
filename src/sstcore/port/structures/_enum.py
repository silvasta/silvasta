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
    "EnumRepr2",
]


from enum import Enum, EnumDict, EnumMeta
from typing import Any, NamedTuple, Self

from ._enumfield import BoundEnumField, EnumField

type EnumId[EnumT: Enum] = EnumT | str | int

type EnumRelation[T: Enum] = tuple[type[T], T] | tuple[type[T]] | tuple[()]


class SstEnumMeta(EnumMeta):
    """
    Tune Enum Meta with some Features

    MEMBER = auto()

    - Self.name = MEMBER
    - Self.value = auto() = 0,..,N
        - len(Self) = N

    Ideas:
    - __bool__: for Options
        EASY: (but how?)
        - index: -> int
        - key: -> str, similar to name
    - short: for LOG_AND_CONTINUE  -> "log", maybe as key?
    - Important: Fallback strategy for Member != auto()!!!

    """

    _walk_for_zero: bool = False
    _zero_indexed: bool = False
    _enum_fields_: dict[str, BoundEnumField[Any, Any]]
    _registered_enums_: list[SstEnumMeta] = []

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
        # metacls: type[_typeshed.Self],
        cls: str,
        bases: tuple[type, ...],
        classdict: EnumDict,
        *,
        zero=False,
        walk=False,
        **kwds: Any,
    ):  # CHECK: ) -> _typeshed.Self:, with: import _typeshed
        """Destroy all custom kwargs and attach Zero"""

        resolved: WalkZero = WalkZero.resolve(walk, zero, bases)

        new_enum_cls = super().__new__(metacls, cls, bases, classdict, **kwds)
        new_enum_cls._zero_indexed = resolved.zero
        new_enum_cls._walk_for_zero = resolved.walk
        new_enum_cls._enum_fields_ = iter_enum_fields(new_enum_cls)  # ty:ignore
        # WARNING:
        # ├╴  Argument to function `iter_enum_fields` is incorrect: Expected `type[Enum]`, found `Self@__new__` ty (invalid-argument-type) [96, 55]
        # AI: is this fine to just ignore? usually what super() or __new__ produces is not properly typed

        if new_enum_cls._enum_fields_:
            metacls._registered_enums_.append(new_enum_cls)

        return new_enum_cls

    def membership(cls, target, /) -> EnumRelation:

        if isinstance(target, cls):
            return (type(target), target)

        if isinstance(target, EnumMeta) and issubclass(target, cls):
            return (target,)

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
                    raise KeyError(f"Unrecognized name: {identifier!r}")
                case _:
                    raise TypeError(f"Unrecognized type: {identifier!r}")

        except (ValueError, KeyError, TypeError) as error:
            if default is None:
                raise type(error)(f"Resolving {cls} failed") from error
        return default

    def validate_fields(cls) -> None:
        """Validate all EnumField descriptors attached to this Enum."""
        for field in cls._enum_fields_.values():
            field.validate()

    def fields_ready(cls) -> bool:
        """Check whether all attached EnumFields have been hydrated."""
        return all(field.is_loaded for field in cls._enum_fields_.values())

    @classmethod
    def validate_all_registered(metacls) -> None:  # noqa:N804
        """Single test-suite hook to hydrate & validate every EnumField in sstcore."""
        for enum_cls in metacls._registered_enums_:
            enum_cls.validate_fields()


def from_zero(name, start, count, last_values):
    """Start from Index Zero"""
    _, _, _ = name, start, last_values
    return count


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


def iter_enum_fields(enum_cls: type[Enum]) -> dict[str, BoundEnumField]:
    """Collect all bound EnumFields across enum_cls and its MRO."""
    fields: dict[str, BoundEnumField] = {}
    for base in reversed(enum_cls.__mro__):
        for name, attr in vars(base).items():
            if isinstance(attr, EnumField):
                fields[name] = getattr(enum_cls, name)
    return fields


def validate_enum_fields(enum_cls: type[Enum]) -> None:
    """Validate all EnumFields on any Enum or IntFlag class."""
    for field in iter_enum_fields(enum_cls).values():
        field.validate()


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


class EnumRepr2(Enum):
    def __repr__(self) -> str:  # CHECK: how that works for Enum
        if attributes := vars(self):
            _vars = [f"{k}={v!r}" for k, v in attributes.items()]
            return f"{type(self).__name__}[{', '.join(_vars)}]"
        return f"{type(self).__name__}{self}"


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
