"""
Stack the output to DTO and next Stack or Result

                                  DependencyLevel.sstcore.brick[0]
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Self

type StackOr[T] = T | Callable[[T, Any], T]


class StackDTO1[T]:
    """For Maximal Dispatch on independent Attributes"""

    attr1: str | None = None
    attr2: str | None = None
    attr3: str | None = None

    def __call__1(self, arg: Any) -> T:
        """Fail... something missing..."""
        cls: type[Self] = type(self)
        match self.attr1, self.attr2, self.attr3:
            case None, None, None:
                raise NotImplementedError

            case None, None, cls():
                raise NotImplementedError

            case None, cls(), None:
                raise NotImplementedError

            case None, cls(), cls():
                raise NotImplementedError

            case cls(), None, None:
                raise NotImplementedError

            case cls(), None, cls():
                raise NotImplementedError

            case cls(), cls(), None:
                raise NotImplementedError

            case cls(), cls(), cls():
                raise NotImplementedError

    def __call__(self, arg: Any) -> T:
        """Dipatch by 2^n_attr separate Functions"""

        match self.attr1, self.attr2, self.attr3:
            case None, None, None:
                raise NotImplementedError

            case None, None, _:
                raise NotImplementedError

            case None, _, None:
                raise NotImplementedError

            case None, _, _:
                raise NotImplementedError

            case _, None, None:
                raise NotImplementedError

            case _, None, _:
                raise NotImplementedError

            case _, _, None:
                raise NotImplementedError

            case _, _, _:
                raise NotImplementedError


type AttrType[Value] = dict[str, Value]

ATTR1: AttrType[int] = {
    "key11": 2,
    "key12": 3,
    "key13": 5,
}

ATTR2: AttrType[str] = {
    "key21": "hello",
    "key22": "bye",
}

ATTR3: AttrType[Callable[[str], str]] = {
    "key31": str.lower,
    "key32": str.capitalize,
    "key33": str.upper,
}


@dataclass  # IDEA: use NamedTuple? maybe easier for stub narrowing
class StackDTO2[Input, T]:
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
        if name in ATTR1:
            return cls(
                attr1=ATTR1[name],
                attr2=self.attr2,
                attr3=self.attr3,
            )
        if name in ATTR2:
            return cls(
                attr1=self.attr1,
                attr2=ATTR2[name],
                attr3=self.attr3,
            )
        if name in ATTR3:
            return cls(
                attr1=self.attr1,
                attr2=self.attr2,
                attr3=ATTR3[name],
            )
        raise AttributeError(f"'{cls.__name__}' has no attribute '{name}'")

    def __call__(self, target: str) -> str:
        string = f"{target} says {self.attr2} to Peter"
        for _ in range(self.attr1 or 1):
            print(string)
        return string


class Handler:
    stack: StackDTO2 = StackDTO2()


handler = Handler()

x = handler.stack.key11.key21.key31("Alice")

y = handler.stack.key21.key32("Bob")

z = handler.stack.key13.key33("Charlie")
