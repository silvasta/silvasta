"""
Inspect arbitrary objects and safely pull out specific attributes

- Extract Type Information from Protocols and Classes for Stub Generation
- Execute functional stack together with Class Builder and Meta Constructors

                             DependencyLevel.sstcore.brick.labor[1]
                                                         ongoing+1

"""


# LATER: compare with port.link._operate or think about separate module here

__all__: list[str] = [
    "AttrFilter",
]


from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field, replace
from typing import Self

from ...port._data import CachedDataclassMeta
from ...port.annotate import anno_presets as _anno
from ...port.empty import VOID, MayBe, MayBeNo
from ._check import Visibility


@dataclass(frozen=True, slots=True)
class AttrFilter(metaclass=CachedDataclassMeta):
    """
    Immutable Flyweight-cached Attribute Acceptance Filter

    - Deduplicat Instances globally from CachedDataclassMeta
    - Chache Constructor or Evolver with equivalent parameters
    - Resolve repeated calls to the same instance in memory

    Precedence (before optional inversion `~filter`):
        1. exclude -> False (explicit blacklist)
        2. include -> True  (explicit whitelist)
        3. mask    -> bool(self.mask & Visibility.classify(name))

    """

    public: bool = True
    private: bool = False
    dunder: bool = False
    include: frozenset[str] = frozenset()
    exclude: frozenset[str] = frozenset()
    invert: bool = False
    mask: Visibility = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Coerce incoming Iterables to frozenset and build Mask"""
        object.__setattr__(self, "include", frozenset(self.include))
        object.__setattr__(self, "exclude", frozenset(self.exclude))
        object.__setattr__(self, "mask", Visibility.combine(*self._flags))

    @property
    def _flags(self) -> tuple[bool, bool, bool]:
        return self.public, self.private, self.dunder

    def __call__(self, name: str, /) -> bool:
        """Predicate check: returns True if attribute should be kept."""
        if name in self.exclude:
            hit = False
        elif name in self.include:
            hit = True
        else:
            hit = bool(self.mask & Visibility.classify(name))
        return hit ^ self.invert

    def mapped[V](self, mapping: Mapping[str, V], /) -> dict[str, V]:
        """Filter Mapping by Keys"""
        return {k: v for k, v in mapping.items() if self(k)}

    def named(self, names: Iterable[str], /) -> Iterator[str]:
        """Yield Matching Attribute Names"""
        for name in names:
            if self(name):
                yield name

    #  LINE: -- Evolver -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __invert__(self) -> Self:
        """Invert the filter acceptance logic (~filter)"""
        return replace(self, invert=not self.invert)

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
        invert: bool | None = None,
    ) -> Self:
        # LATER: do this better, some VOID and set |&^ tricks
        """Create new AttrFilter with updated flags or merged sets"""

        _new_include = self.include if include is None else frozenset(include)

        if add_include:
            _added_in = frozenset(add_include)
            _new_include = _new_include | _added_in
        else:
            _added_in = frozenset()

        _new_exclude = (
            (self.exclude - _added_in)
            if exclude is None
            else frozenset(exclude)
        )
        if add_exclude:
            _added_ex = frozenset(add_exclude)
            _new_exclude = _new_exclude | _added_ex
            _new_include = _new_include - _added_ex

        return replace(
            self,
            public=self.public if public is None else public,
            private=self.private if private is None else private,
            dunder=self.dunder if dunder is None else dunder,
            include=_new_include,
            exclude=_new_exclude,
            invert=self.invert if invert is None else invert,
        )

    def excluding(self, *names: str) -> Self:
        """Evolve with additional blacklisted names"""
        return self if not names else self.evolve(add_exclude=names)

    def including(self, *names: str) -> Self:
        """Evolve with additional whitelisted names"""
        return self if not names else self.evolve(add_include=names)

    def showing(self, visibility: Visibility | int, /) -> Self:
        """Enable additional Visibility flags"""
        return (
            self
            if (vis := Visibility.resolve(visibility)) == self.mask
            else self.evolve(
                public=self.public or bool(vis & Visibility.PUBLIC),
                private=self.private or bool(vis & Visibility.PRIVATE),
                dunder=self.dunder or bool(vis & Visibility.DUNDER),
            )
        )

    #  LINE: -- Constructor -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    @classmethod
    def masked(
        cls,
        visibility: Visibility | int,
        /,
        *,
        include: Iterable[str] = (),
        exclude: Iterable[str] = (),
        invert: bool = False,
    ) -> Self:
        """Construct an AttrFilter directly from a Visibility bitmask."""
        vis: Visibility = Visibility.resolve(visibility)
        return cls(
            public=bool(vis & Visibility.PUBLIC),
            private=bool(vis & Visibility.PRIVATE),
            dunder=bool(vis & Visibility.DUNDER),
            include=frozenset(include),
            exclude=frozenset(exclude),
            invert=invert,
        )

    @classmethod
    def protocol(
        cls,
        *,
        include_dunders: MayBe[Iterable[str]] = VOID,
        exclude: Iterable[str] = (),
    ) -> Self:
        """Extract Protocol or Stubs: public + designated interface dunders"""
        return cls(
            public=True,
            private=False,
            dunder=False,
            include=frozenset(
                _anno.DUNDERS if include_dunders is VOID else include_dunders
            ),
            exclude=frozenset(exclude),
        )

    @classmethod
    def forge(cls, *, exclude: Iterable[str] = ()) -> Self:
        """Public attributes + standard calling/context/iterator dunders"""
        return cls(
            include=frozenset(_anno.CALLING),
            exclude=frozenset(exclude),
        )

    @classmethod
    def calling(cls, *, exclude: Iterable[str] = ()) -> Self:
        """Public attributes + direct invocation dunders (__call__, __getitem__)"""
        return cls(
            include=frozenset(("__call__", "__getitem__")),
            exclude=frozenset(exclude),
        )

    @classmethod
    def resolve(
        cls,
        filter: MayBeNo[Self] = VOID,
        /,
        *,
        exclude: Iterable[str] = (),
    ) -> Self:
        """Resolve a MayBeNo[AttrFilter] parameter into an active AttrFilter.

        - VOID       -> cls.default(exclude=exclude)
        - None       -> cls.empty(exclude=exclude)
        - AttrFilter -> filter.excluding(*exclude)
        """
        if filter is VOID:
            return cls.default(exclude=exclude)
        if filter is None:
            return cls.empty(exclude=exclude)
        return filter.excluding(*exclude)

    @classmethod
    def default(cls, *, exclude: Iterable[str] = ()) -> Self:
        """Public attributes only"""
        return cls(exclude=frozenset(exclude))

    @classmethod
    def empty(cls, *, exclude: Iterable[str] = ()) -> Self:
        """Include everything except an explicit blacklist"""
        return cls(
            public=True,
            private=True,
            dunder=True,
            exclude=frozenset(exclude),
        )
