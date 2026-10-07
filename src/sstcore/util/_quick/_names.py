"""
GetNames - provide names for testing

-
"""

import itertools
from collections.abc import Iterator, Sequence
from typing import Literal, Self


class GetNames:
    defaults: list[str] = [
        "Alice",
        "Peter",
        "Chris",
        "Diana",
    ]
    type Modes = Literal["cyclic", "finite"]

    def __init__(
        self,
        names: Sequence[str] | None = None,
        mode: GetNames.Modes = "finite",
        fallback: str | None = None,
    ):
        self.names: list[str] = list(names) if names else self.defaults
        self.mode: self.Modes = mode
        self.fallback: str | None = fallback
        self._count: int = 0
        self._iterator: Iterator[str] = self._setup_stream()

    @classmethod
    def cyclic(cls, names: list[str] | None = None) -> Self:
        return cls(names, mode="cyclic")

    def _setup_stream(self) -> Iterator[str]:
        match self.mode:
            case "finite":
                return iter(self.names)
            case "cyclic":
                return itertools.cycle(self.names)

    @property
    def _count_view(self) -> str:
        lap, count = divmod(self._count - 1, len(self))
        return f"{f'{lap}][' if lap else ''}{count + 1}/{len(self)}"

    @property
    def _rest_view(self) -> str:
        return f"[{self.rest}]" if self.rest >= 0 else ""

    def __str__(self):
        return f"{type(self).__name__}[{self._count_view}]{self._rest_view}"

    def __repr__(self):
        return f"{self}(mode={self.mode!r}, items={len(self.names)})"

    def __len__(self):
        return len(self.names)

    @property
    def rest(self) -> int:
        return len(self) - self._count

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> str:
        self._count += 1  # ignore fails on StopIteration
        return (
            next(self._iterator)
            if self.fallback is None
            else next(self._iterator, self.fallback)
        )

    def __call__(self) -> str:
        return self.__next__()

    def reset(self) -> None:
        self._count = 0
        self._iterator = self._setup_stream()

    def clone(self) -> Self:
        return type(self)(self.names, self.mode, self.fallback)


if __name__ == "__main__":
    c_names: GetNames = GetNames.cyclic()
    f_names: GetNames = GetNames()

    print("--- -- ---" * 5)
    print("start of c_names")
    print("--- -- ---" * 5)
    for _ in range(10):
        print(c_names, c_names())

    print("end of c_names")

    print("\n", "--- -- ---" * 5)
    print("start of f_names")
    print("--- -- ---" * 5)
    try:
        for _i in range(10):
            print(f_names, f_names())
    except StopIteration:
        print(f"End at StopIteration: {_i}")
    print("end of f_names")

    print("\n", "--- -- ---" * 5)
    print("start of f_names")
    print("--- -- ---" * 5)
    for name in f_names:
        print(f_names, name)
    print("end of f_names")

    names_with_fallback = GetNames(fallback="EndOfNames")

    print("\n", "--- -- ---" * 5)
    print("start of f_names")
    print("--- -- ---" * 5)
    for _ in range(10):
        print(names_with_fallback, names_with_fallback())
    print("end of f_names")
