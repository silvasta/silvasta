"""
Govern the Shape and Structure of the Strict and Reliable Container

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "EnumZero",
    "EnumId",
    # view
    "EnumRepr",
    "EnumStr",
]


from enum import Enum, EnumMeta, auto
from typing import Any, Literal, NamedTuple, Self, reveal_type

#  LINE: -- Views -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class EnumStr1(Enum):
    def __str__(self) -> str:
        return f"{self.name.capitalize()}"


class EnumStr2(Enum):
    def __str__(self):
        return self.name


class EnumRepr1(Enum):
    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.value}]::{self}"


class _EnumRepr2(Enum):
    def __repr__(self) -> str:  # CHECK: how that works for Enum
        if attributes := vars(self):
            _vars = [f"{k}={v!r}" for k, v in attributes.items()]
            return f"{type(self).__name__}[{', '.join(_vars)}]"
        return f"{type(self).__name__}{self}"


EnumStr = EnumStr2
EnumRepr = EnumRepr1


class SstEnumMeta(EnumMeta):
    _is_zero_indexed: bool

    @classmethod
    def __prepare__(_mcls, cls, bases, **kwargs):  # noqa:N804
        enum_dict = super().__prepare__(cls, bases, **kwargs)
        if kwargs.get("zero", False):
            enum_dict["_generate_next_value_"] = staticmethod(
                lambda name, start, count, last_values: count
            )
        return enum_dict

    def __new__(metacls, cls, bases, classdict, **kwargs):
        is_zero: bool = kwargs.pop("zero", False)
        new_enum_cls = super().__new__(
            metacls, cls, bases, classdict, **kwargs
        )
        new_enum_cls._is_zero_indexed = is_zero
        return new_enum_cls


#  LINE: -- Index -- -- - -- -- - -- -- - -- -- - -- -- - -- --


type EnumId[EnumT] = EnumT | str | int


type _EnumRelationResult = Literal["unit", "cls", "fail"]


class _EnumRelation[EnumT: Enum](NamedTuple):
    result: _EnumRelationResult
    cls: type[EnumT] | None = None
    self: EnumT | None = None


type EnumRelation[T: ResolvingEnum] = (
    tuple[type[T], T] | tuple[type[T]] | tuple
)


class ResolvingEnum(Enum):
    """Match by Int, Str and Slice"""

    @classmethod
    def membership[T: ResolvingEnum](
        cls, target: T | type[T] | Any, /
    ) -> EnumRelation[T]:
        """Check if target is Enum class or instance"""

        if isinstance(target, cls):
            reveal_type(target)
            return (type(target), target)

        if isinstance(target, type) and issubclass(target, cls):
            reveal_type(target)
            return (target,)

        return ()

    @classmethod
    def resolve(cls, identifier: EnumId[Self], /, default=None) -> Self:
        """Map [int|str|EnumT] to EnumT, default or Raise"""
        try:
            match identifier:
                case cls():
                    return identifier

                case int() as index:
                    return cls(index)

                case str() as name:
                    return cls[name.upper()]  # WARN: does this hold?
                case _:
                    raise ValueError(f"Unrecognized type: {type(identifier)}")

        except (ValueError, KeyError) as error:  # WARN: IndexError?
            if default is None:
                message = f"Mapping {cls} failed: {identifier=}"
                raise Exception(message) from error  # TODO: EnumError?
        return default


class Enum0(Enum, metaclass=SstEnumMeta):
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

    """

    # AI: here was before the _generate_next_value_, until I realised it fails for derived classes...


class EnumZero(ResolvingEnum, Enum0):
    """Set Count to Zero and Match by Int, Str and Slice"""


if __name__ == "__main__":

    class TestEnum(Enum):
        BLACK = auto()
        WHITE = auto()

    class TestFail(Enum):
        GREY = auto()
        BLUE = auto()

    def print_vars(target, /):
        print("\n", "\n".join(["--- " * 5]), "\n")
        lines = "\n".join(f" - {k}:={v}" for k, v in vars(target).items())
        print(lines)
        print("\n", "\n".join(["--- " * 5]), "\n")

    print_vars(Enum0)

    class MyEnum0(Enum0, EnumStr1, EnumRepr1, zero=True):
        RED = auto()
        BLUE = auto()
        GREEN = auto()

    print_vars(Enum0)

    print(MyEnum0)
    for member in MyEnum0:
        print(f"{member}({member.name=},{member.value=})->{member!r}")
