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


from enum import Enum, EnumMeta
from typing import NamedTuple, Self

type EnumId[EnumT: Enum] = EnumT | str | int


type EnumRelation[T: Enum] = tuple[type[T], T] | tuple[type[T]] | tuple[()]


class SstEnumMeta(EnumMeta):
    """
    Set Count to Zero

    MEMBER = auto()

    - Self.name = MEMBER
    - Self.value = auto() = 0,..,N
        - len(Self) = N

    Ideas:
    - __bool__: for Options
    - index: -> int
    - key: -> str, similar to name
    - short: for LOG_AND_CONTINUE  -> "log", maybe as key?

    """  # LATER:  better description

    _is_zero_indexed: bool = False
    _walk_for_zero: bool = False

    @classmethod
    def __prepare__(_mcls, cls, bases, **kwargs):  # noqa:N804

        enum_dict = super().__prepare__(cls, bases, **kwargs)

        if WalkZero.resolve(bases, kwargs).zero:
            enum_dict["_generate_next_value_"] = staticmethod(from_zero)

        return enum_dict

    def __new__(metacls, cls, bases, classdict, **kwargs):
        """Destroy all custom kwargs and attach Zero"""

        resolved: WalkZero = WalkZero.resolve(bases, kwargs)

        kwargs.pop("zero", None)
        kwargs.pop("walk", None)

        new_enum_cls = super().__new__(
            metacls, cls, bases, classdict, **kwargs
        )
        new_enum_cls._is_zero_indexed = resolved.zero
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
    """Later: add good doc"""
    return count


class WalkZero(NamedTuple):
    walk: bool
    zero: bool

    @classmethod
    def resolve(cls, bases: tuple[type, ...], kwargs: dict) -> Self:
        """Resolve inherited walk and zero flags from kwargs and bases"""
        walk: bool = kwargs.get(
            "walk", any(getattr(b, "_walk_for_zero", False) for b in bases)
        )
        zero: bool = kwargs.get(
            "zero",
            walk and any(getattr(b, "_is_zero_indexed", False) for b in bases),
        )
        return cls(walk, zero)


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
