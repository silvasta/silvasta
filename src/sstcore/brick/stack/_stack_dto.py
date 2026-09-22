"""
Idea with DTO and written out

- Temporary until split

"""

# NEXT: implement

__all__: list[str] = [
    "MulitStackDTO",
]

from dataclasses import dataclass
from typing import Any, Self

from . import ___data as data


@dataclass  # IDEA: use NamedTuple? maybe easier for stub narrowing
class MulitStackDTO[Input, T]:
    """Attach Stacking by adding Mappings"""

    # IDEA: some class constructor that automatically generates the following:
    # - for each inserted mapping M_i[str,T_i]:
    #   - cls.attr_i:T_i
    #   - if name in M_i: return cls(...,attr_i=M_i[name],...)
    # - injected function for call F[T_i,...]
    # - provide recipe for writing pyi
    # - if possible narrow by: cls.attr_1!=None

    attr1: Any | None = None
    attr2: Any | None = None
    attr3: Any | None = None

    def __getattr__(self, name: str) -> Self:
        cls: type[Self] = type(self)
        if name in data.ATTR1:
            return cls(
                attr1=data.ATTR1[name],
                attr2=self.attr2,
                attr3=self.attr3,
            )
        if name in data.ATTR2:
            return cls(
                attr1=self.attr1,
                attr2=data.ATTR2[name],
                attr3=self.attr3,
            )
        if name in data.ATTR3:
            return cls(
                attr1=self.attr1,
                attr2=self.attr2,
                attr3=data.ATTR3[name],
            )
        raise AttributeError(f"'{cls.__name__}' has no attribute '{name}'")

    def __call__(self, target: str) -> str:
        string = f"{target} says {self.attr2} to Peter"
        for _ in range(self.attr1 or 1):
            print(string)
        return string
