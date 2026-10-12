"""
Govern the Shape and Structure of the Strict and Reliable Container

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "SstEnumMeta",
    "EnumRelation",
    "EnumId",
    # view
    "EnumStr",
    "EnumRepr",
    #
    "EnumStr1",
    "EnumStr2",
    "EnumRepr1",
    "EnumRepr2",
]


from enum import Enum, EnumDict, EnumMeta
from typing import Any, NamedTuple, Self

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

        return new_enum_cls

    def membership(cls, target, /) -> EnumRelation:
        """Check if target is Enum class or instance"""

        if isinstance(target, cls):
            return (type(target), target)

        if isinstance(target, EnumMeta) and issubclass(target, cls):
            return (target,)

        return ()

    def resolve(cls, identifier: EnumId, /, default=None):
        """Map [int|str|EnumT] to BaseEnum derivative, default or Raise"""
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


def from_zero(name, start, count, last_values):
    """Set Count to Zero"""
    _, _, _ = name, start, last_values
    return count


class WalkZero(NamedTuple):
    walk: bool
    zero: bool

    @classmethod
    def resolve(cls, walk: bool, zero: bool, bases: tuple[type, ...]) -> Self:
        """Resolve inherited walk and zero flags from kwargs and bases"""

        _walked_walk: bool = walk or any(
            getattr(base, "_walk_for_zero", False) for base in bases
        )

        _zero_or_walked_zero: bool = zero or (
            walk
            and any(getattr(base, "_zero_indexed", False) for base in bases)
        )
        return cls(_walked_walk, _zero_or_walked_zero)


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
