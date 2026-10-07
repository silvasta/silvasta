"""
Govern the Shape and Structure of the Strict and Reliable Container

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "EnumZero",
    # view
    "EnumRepr",
    "EnumStr",
]


from enum import Enum
from typing import Any, Literal, Self

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


#  LINE: -- Index -- -- - -- -- - -- -- - -- -- - -- -- - -- --


type EnumSlice[EnumT] = EnumId[EnumT] | slice


class SlicingEnum(Enum):
    # TASK: ok that with the slice is not even so easy...
    def __getitem__(self, key: EnumSlice):
        raise NotImplementedError(key)


type EnumId[EnumT] = EnumT | str | int


class Enum0(Enum):
    # IDEA: one step more!
    # ignore value=auto()
    # -> directly attach (paramerized) target
    # e.g. LAZY = LazyField
    # for identification:
    # - Enum0.key->str
    # - Enum0.index->int
    """Set Count to Zero"""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> int:
        """Count the Enum Index starting at Zero"""
        return count


class ResolvingEnum(Enum):
    """Match by Int, Str and Slice"""

    @classmethod
    def includes(
        cls, target: Self | type[Self] | Any, /
    ) -> (
        tuple[Literal["unit"], Self]
        | tuple[Literal["cls"], type[Self]]
        | tuple[Literal["fail"], None]
    ):
        """Check if target is Enum class or instance"""

        if isinstance(target, cls):
            return "unit", target

        if isinstance(target, type) and issubclass(target, cls):
            return "cls", target

        return "fail", None

    @classmethod
    def identify(cls, identifier: str | int | Self, /, default=None) -> Self:
        """Map [int|str|EnumT] to EnumT, Default or Raise"""
        try:
            match identifier:
                case cls():
                    return identifier

                case int() as index:
                    return cls(index)

                case str() as name:
                    return cls[name.upper()]
                case _:
                    raise ValueError(f"Unrecognized type: {type(identifier)}")

        except (ValueError, KeyError) as error:
            if default is None:
                message = f"Mapping {cls} failed: {identifier=}"
                raise ValueError(message) from error
        return default


class EnumZero(ResolvingEnum, Enum0):
    """Set Count to Zero and Match by Int, Str and Slice"""
