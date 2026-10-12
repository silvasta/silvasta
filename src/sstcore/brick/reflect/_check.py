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

from collections.abc import Callable
from typing import Generic, NamedTuple, Protocol


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


class AttrFilter(NamedTuple):  # NEXT: build more proper filter!
    """Collect Flags and provide corresponding Filter"""

    public: bool = True
    private: bool = False
    dunder: bool = False

    def get_filter(self) -> Callable[[str], bool]:
        """Separate by public/private/dunder with dunder not in private"""
        match self.public, self.private, self.dunder:
            case (False, False, False):
                raise ValueError("All flags set zero! No result!")

            case (False, False, True):
                return lambda attr: is_dunder(attr)

            case (False, True, False):
                return lambda attr: is_private(attr) and not is_dunder(attr)

            case (False, True, True):
                return lambda attr: is_private(attr)

            case (True, False, False):
                return lambda attr: not is_private(attr)

            case (True, False, True):
                return lambda attr: is_dunder(attr) or not is_private(attr)

            case (True, True, False):
                return lambda attr: not is_dunder(attr)

            case (True, True, True):
                return lambda _attr: True
