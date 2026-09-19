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
from typing import Self

#  LINE: -- Views -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class EnumStr1(Enum):
    name: str

    def __str__(self) -> str:
        return f"{self.name.capitalize()}"


class EnumStr2(Enum):
    name: str

    def __str__(self):
        return self.name


class EnumRepr1(Enum):
    value: int

    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.value}]::{self}"


EnumStr = EnumStr2
EnumRepr = EnumRepr1


#  LINE: -- Index -- -- - -- -- - -- -- - -- -- - -- -- - -- --


type EnumId[EnumT] = EnumT | str | int

type EnumSlice[EnumT] = EnumId[EnumT] | slice


class Enum0(Enum):
    """Set Count to Zero"""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> int:
        """Count the Enum Index starting at Zero"""
        return count


class SlicingEnum(Enum):
    # TASK: slicing
    def __getitem__(self, key: EnumSlice):
        raise NotImplementedError(key)


class ResolvingEnum(Enum):
    """Match by Int, Str and Slice"""

    def resolve(
        self, identifier: EnumId[Self], default: Self | None = None
    ) -> Self:
        # TASK: ok that with the slice is not even so easy...
        """Map [int|str|EnumT] to EnumT, Default or Raise"""
        enum = type(self)
        try:
            match identifier:
                case enum():
                    return identifier

                case int() as index:
                    return enum(index)

                case str() as name:
                    return enum[name.upper()]

                case _:
                    raise ValueError(f"Unrecognized type: {type(identifier)}")

        except (ValueError, KeyError) as error:
            if default is None:
                raise ValueError(
                    f"Mapping {enum} failed: {identifier=}"
                ) from error
        return default


class EnumZero(ResolvingEnum, Enum0):
    """Set Count to Zero and Match by Int, Str and Slice"""
