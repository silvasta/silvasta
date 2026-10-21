"""
Inspect arbitrary objects and safely pull out specific attributes

- Extract Type Information from Protocols and Classes for Stub Generation
- Execute functional stack together with Class Builder and Meta Constructors

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "is_private",
    "is_dunder",
    "is_protocol",
    "is_private_not_calling",
    "is_typing_generic",
    #
    "AttrFilter",
]

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field, replace
from typing import Generic, Protocol, Self


def is_private(attr: str, /) -> bool:
    return attr.startswith("_")


def is_dunder(attr: str, /) -> bool:
    return attr.startswith("__") and attr.endswith("__")


def is_protocol(cls: type) -> bool:
    """Check type first to avoid TypeError on second call"""
    return (
        isinstance(cls, type)
        and issubclass(cls, Protocol)
        and getattr(cls, "_is_protocol", False)
    )


def is_private_not_calling(attr: str) -> bool:  # TODO: resolve by AttrFilter?
    exclude: set[str] = {"__call__", "__getitem__"}
    return attr.startswith("_") and attr not in exclude


def is_typing_generic(cls: type) -> bool:
    return cls in (object, Protocol, Generic)


PROTOCOL_DUNDERS: frozenset[str] = frozenset(
    {
        "__call__",
        "__getitem__",
        "__iter__",
        "__enter__",
        "__exit__",
        "__next__",
        "__await__",
        "__aiter__",
        "__anext__",
    }
)


@dataclass(frozen=True, slots=True)
class AttrFilter:
    """High-performance attribute acceptance filter.

    Precedence:
        1. include -> True
        2. exclude -> False
        3. dunder  -> self.dunder
        4. private -> self.private
        5. public  -> self.public
    """

    public: bool = True
    private: bool = False
    dunder: bool = False
    include: frozenset[str] = field(default_factory=frozenset)
    exclude: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        """Coerce any incoming iterable (lists/sets) to immutable frozensets"""
        if not isinstance(self.include, frozenset):
            object.__setattr__(self, "include", frozenset(self.include))
        if not isinstance(self.exclude, frozenset):
            object.__setattr__(self, "exclude", frozenset(self.exclude))

    def evolve(
        self,
        *,
        public: bool | None = None,
        private: bool | None = None,
        dunder: bool | None = None,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
        add_include: Iterable[str] | None = None,
        add_exclude: Iterable[str] | None = None,
    ) -> Self:
        """Create a new AttrFilter with updated flags or merged sets."""
        _new_include = self.include if include is None else frozenset(include)
        if add_include:
            _new_include = _new_include | frozenset(add_include)

        _new_exclude = self.exclude if exclude is None else frozenset(exclude)
        if add_exclude:
            _new_exclude = _new_exclude | frozenset(add_exclude)

        return replace(
            self,
            public=self.public if public is None else public,
            private=self.private if private is None else private,
            dunder=self.dunder if dunder is None else dunder,
            include=_new_include,
            exclude=_new_exclude,
        )

    def excluding(self, *names: str) -> Self:
        """Return a copy with additional excluded names."""
        return replace(self, exclude=self.exclude | frozenset(names))

    def including(self, *names: str) -> Self:
        """Return a copy with additional whitelisted names."""
        return replace(self, include=self.include | frozenset(names))

    def __call__(self, name: str, /) -> bool:
        """Predicate check: returns True if attribute should be kept."""
        if name in self.include:
            return True
        if name in self.exclude:
            return False
        if is_dunder(name):
            return self.dunder
        if name.startswith("_"):
            return self.private
        return self.public

    def filter_names(self, names: Iterable[str]) -> Iterator[str]:
        """Yield only matching attribute names."""
        for name in names:
            if self(name):
                yield name

    def filter_dict[V](self, mapping: Mapping[str, V]) -> dict[str, V]:
        """Filter a dictionary/mapping by attribute keys."""
        return {k: v for k, v in mapping.items() if self(k)}

    @classmethod
    def default(cls) -> Self:
        """Public attributes only."""
        return cls(public=True, private=False, dunder=False)

    @classmethod
    def all(cls, *, exclude: Iterable[str] = ()) -> Self:
        """Include everything except an explicit blacklist."""
        return cls(
            public=True, private=True, dunder=True, exclude=frozenset(exclude)
        )

    @classmethod
    def protocol(
        cls,
        *,
        include_dunders: Iterable[str] = PROTOCOL_DUNDERS,
        exclude: Iterable[str] = (),
    ) -> Self:
        """Standard stub/protocol extractor: public methods + designated interface dunders."""
        return cls(
            public=True,
            private=False,
            dunder=False,
            include=frozenset(include_dunders),
            exclude=frozenset(exclude),
        )
