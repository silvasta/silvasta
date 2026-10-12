from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import IntFlag, auto
from typing import Self


class Visibility(IntFlag):
    PUBLIC = auto()  # 1  foo
    PRIVATE = auto()  # 2  _foo
    DUNDER = auto()  # 4  __foo__
    HIDDEN = PRIVATE | DUNDER  # 6
    ALL = PUBLIC | PRIVATE | DUNDER  # 7


def attr_kind(name: str, /) -> Visibility:
    if name.startswith("__") and name.endswith("__"):
        return Visibility.DUNDER
    if name.startswith("_"):
        return Visibility.PRIVATE
    return Visibility.PUBLIC


@dataclass(frozen=True, slots=True)
class AttrFilter:
    """Gate: exclude wins, include overrides kind, else visibility bitmask."""

    public: bool = True
    private: bool = False
    dunder: bool = False
    include: frozenset[str] = field(default_factory=frozenset)
    exclude: frozenset[str] = field(default_factory=frozenset)
    invert: bool = False
    _mask: int = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        include: frozenset[str] = frozenset(self.include)
        exclude: frozenset[str] = frozenset(self.exclude)
        mask: int = (
            (Visibility.PUBLIC if self.public else 0)
            | (Visibility.PRIVATE if self.private else 0)
            | (Visibility.DUNDER if self.dunder else 0)
        )
        if mask == 0 and not include:
            raise ValueError("All flags set zero! No result!")
        object.__setattr__(self, "include", include)
        object.__setattr__(self, "exclude", exclude)
        object.__setattr__(self, "_mask", int(mask))

    def __call__(self, name: str, /) -> bool:
        if name in self.exclude:
            hit = False
        elif name in self.include:
            hit = True
        else:
            hit = bool(self._mask & attr_kind(name))
        return hit ^ self.invert

    def allowing(self, *names: str) -> Self:
        return self._evolve(include=self.include | frozenset(names))

    def denying(self, *names: str) -> Self:
        return self._evolve(exclude=self.exclude | frozenset(names))

    def showing(self, vis: Visibility) -> Self:
        return self._evolve(
            public=bool(vis & Visibility.PUBLIC) or self.public,
            private=bool(vis & Visibility.PRIVATE) or self.private,
            dunder=bool(vis & Visibility.DUNDER) or self.dunder,
        )

    def __invert__(self) -> Self:
        return self._evolve(invert=not self.invert)

    def _evolve(self, **changes) -> Self:
        data = {
            "public": self.public,
            "private": self.private,
            "dunder": self.dunder,
            "include": self.include,
            "exclude": self.exclude,
            "invert": self.invert,
        }
        data.update(changes)
        return type(self)(**data)

    @classmethod
    def of(
        cls,
        vis: Visibility,
        /,
        *,
        include: Iterable[str] = (),
        exclude: Iterable[str] = (),
    ) -> Self:
        return cls(
            public=bool(vis & Visibility.PUBLIC),
            private=bool(vis & Visibility.PRIVATE),
            dunder=bool(vis & Visibility.DUNDER),
            include=frozenset(include),
            exclude=frozenset(exclude),
        )


DUNDER_CALLING: frozenset[str] = frozenset(
    {
        "__call__",
        "__getitem__",
        "__iter__",
        "__enter__",
        "__exit__",
    }
)
DUNDER_OBJECT: frozenset[str] = frozenset(
    {
        "__init__",
        "__new__",
        "__dict__",
        "__weakref__",
        "__doc__",
        "__module__",
        "__annotations__",
        "__subclasshook__",
    }
)
SUNDER_PROTOCOL: frozenset[str] = frozenset(
    {
        "_is_protocol",
        "_is_runtime_protocol",
    }
)

SURFACE = AttrFilter()  # public
FORGE = AttrFilter(include=DUNDER_CALLING)  # public + calling dunders
KEEP_CALLING = AttrFilter(include=frozenset({"__call__", "__getitem__"}))
