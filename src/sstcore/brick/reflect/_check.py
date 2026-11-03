"""
Inspect arbitrary objects and safely pull out specific attributes

- Extract Type Information from Protocols and Classes for Stub Generation
- Execute functional stack together with Class Builder and Meta Constructors

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "AttrFilter",
    "Visibility",
    # checks
    "is_private",
    "is_dunder",
    "is_protocol",
    "is_private_not_calling",
    "is_typing_generic",
    # presets
    "PROTOCOL_DUNDERS",
    "DUNDER_CALLING",
    "DUNDER_OBJECT",
    "SUNDER_PROTOCOL",
    "KEEP_CALLING",
]

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field, replace
from enum import IntFlag, auto
from typing import Generic, Protocol, Self

from ...port.empty import VOID, MayBe, MayBeNo

# LATER: compare with port.link._operate or think about separate module here


class Visibility(IntFlag):
    NONE = 0
    PUBLIC = auto()
    PRIVATE = auto()
    DUNDER = auto()
    HIDDEN = PRIVATE | DUNDER
    ALL = PUBLIC | PRIVATE | DUNDER

    @classmethod
    def classify(cls, name: str, /) -> Visibility:
        """Map Visibility according to _Attribute __Name__"""
        if is_dunder(name):
            return cls.DUNDER
        if is_private(name):
            return cls.PRIVATE
        return cls.PUBLIC

    @classmethod
    def combine(
        cls, public: bool, private: bool, dunder: bool, /
    ) -> Visibility:
        """Merge all 3 Flags to Visibility"""
        mask: Visibility = cls.NONE
        if public:
            mask |= cls.PUBLIC
        if private:
            mask |= cls.PRIVATE
        if dunder:
            mask |= cls.DUNDER
        return mask

    @classmethod
    def resolve(cls, vis: int, /) -> Visibility:
        # LATER: add some views, for member, combined member, and error
        """Cast Int to Visibility or show clear Error"""
        if 0 <= vis <= (max := 2 ** len(cls) - 1):
            return cls(vis)
        member: Mapping = cls.__members__
        raise ValueError(f"Bad Flag Number: {vis}, {max=}, {member=}")


def is_private(attr: str, /) -> bool:
    return attr.startswith("_")


def is_dunder(attr: str, /) -> bool:
    return len(attr) > 4 and attr.startswith("__") and attr.endswith("__")


def is_protocol(cls: type) -> bool:
    """Check type first to avoid TypeError on second call"""
    return (
        isinstance(cls, type)
        and issubclass(cls, Protocol)
        and getattr(cls, "_is_protocol", False)
    )


def is_typing_generic(cls: type) -> bool:
    return cls in (object, Protocol, Generic)


#  LINE: -- Main Class -- -- - -- -- - -- -- - -- -- - -- -- - -- --


type Key[Filter: type[AttrFilter]] = tuple[str, type[Filter], frozenset]
type Cache[Filter: type[AttrFilter]] = dict[Key[Filter], Filter]
CACHE: Cache = {}


@dataclass(frozen=True, slots=True)
class AttrFilter:
    """
    High-performance attribute acceptance filter

    Precedence (before optional inversion):
        1. exclude -> False
        2. include -> True
        3. kind    -> bool(self._mask & attr_kind(name))

    """

    public: bool = True
    private: bool = False
    dunder: bool = False
    include: frozenset[str] = field(default_factory=frozenset)
    exclude: frozenset[str] = field(default_factory=frozenset)
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

    #  LINE: -- Filtering -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __call__(self, name: str, /) -> bool:
        # LATER: check if overload with Iterable[str] is worth
        """Predicate check: returns True if attribute should be kept."""
        if name in self.exclude:
            hit = False
        elif name in self.include:
            hit = True
        else:
            hit = bool(self.mask & Visibility.classify(name))
        return hit ^ self.invert

    def named(self, names: Iterable[str], /) -> Iterator[str]:
        """Yield Matching Attribute Names"""
        for name in names:
            if self(name):
                yield name

    def mapped[V](self, mapping: Mapping[str, V], /) -> dict[str, V]:
        """Filter Mapping by Keys"""
        return {k: v for k, v in mapping.items() if self(k)}

    #  LINE: -- Evolving -- -- - -- -- - -- -- - -- -- - -- -- - -- --

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

    #  LINE: -- Constructing -- -- - -- -- - -- -- - -- -- - -- -- - -- --

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
        include: frozenset[str] = (
            PROTOCOL_DUNDERS
            if include_dunders is VOID
            else frozenset(include_dunders)
        )
        return cls(
            public=True,
            private=False,
            dunder=False,
            include=include,
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
    def _cached(cls, kind: str, /, **flags) -> Self:
        """Build or fetch cached preset instance for this subclass"""
        key: Key = kind, cls, frozenset(flags.get("exclude", ()))
        if key not in CACHE:
            CACHE[key] = cls(**flags)
        return CACHE[key]

    @classmethod
    def default(cls, *, exclude: Iterable[str] = ()) -> Self:
        """Public attributes only"""
        return cls._cached("default", exclude=frozenset(exclude))

    @classmethod
    def empty(cls, *, exclude: Iterable[str] = ()) -> Self:
        """Include everything except an explicit blacklist"""
        return cls._cached(
            "empty",
            public=True,
            private=True,
            dunder=True,
            exclude=frozenset(exclude),
        )


# AI: the presets are desired here below (Python 3.14+)
# - just keep them at the bottom and the main class as inital view of the module

#  LINE: -- FrozenSet Presets -- -- - -- -- - -- -- - -- -- - -- -- - -- --

# LATER: compare with port.link._operate or another definition layer in the port

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


#  LINE: -- Singleton Presets  and Cache -- -- - -- -- - -- -- - -- -- - -- -- -


# LATER: resolve to some useful combination of presets

FORGE = AttrFilter(include=DUNDER_CALLING)
KEEP_CALLING = AttrFilter(include=frozenset({"__call__", "__getitem__"}))
is_private_not_calling: AttrFilter = ~KEEP_CALLING
