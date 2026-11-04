"""
Inspect arbitrary objects and safely pull out specific attributes

- Extract Type Information from Protocols and Classes for Stub Generation
- Execute functional stack together with Class Builder and Meta Constructors

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "Visibility",
    # checks
    "is_private",
    "is_dunder",
    "is_protocol",
    "is_typing_generic",
]


# NOTE: is_private_not_calling: AttrFilter = ~KEEP_CALLING
# - removed as it now can easily be pulled from AttrFilter
# REMOVE: the note above when everywhere established

from collections.abc import Mapping
from enum import IntFlag, auto
from typing import Generic, Protocol

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
