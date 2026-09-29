"""
Tree Printer

- temporary module
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, Self


class SimpleTree(Protocol):
    """Protocol for any hierarchical tree node."""

    @property
    def name(self) -> str: ...
    @property
    def id(self) -> str | None: ...
    @property
    def display_label(self) -> str: ...
    @property
    def identifier(self) -> Any: ...
    @property
    def branches(self) -> Sequence[SimpleTree]: ...


@dataclass(frozen=True)
class SimpleTreeNode:
    """Build Node with 0..N subnodes each with own subnodes"""

    name: str
    id: str | None = None
    branches: Sequence[Self] = field(default_factory=list)

    @property
    def display_label(self) -> str:
        """Show public representation e.g. in Selector or Visualization"""
        return self.name

    @property
    def identifier(self):
        """Provide value that allows identification (No test for uniqness here!)"""
        return self.id


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True)
class MroTreeNode1(SimpleTreeNode):
    """Represent an Inheritance Tree, annotated with MRO order.G3"""

    source: type = field(default=object)
    mro_index: int | None = field(default=None)

    @property
    def identifier(self) -> Any:
        return self.source

    @property
    def display_label(self) -> str:
        """Shows ClassName and its actual MRO resolution index."""
        if self.mro_index is not None:
            return f"{self.name} [dim italic](MRO: {self.mro_index})[/]"
        return self.name

    @classmethod
    def build(
        cls, target: type, _root_mro: tuple[type, ...] | None = None
    ) -> Self:
        """
        Recursively build the tree using __bases__.

        Matches the classes against the root target's MRO.
        """
        if _root_mro is None:
            _root_mro = target.__mro__

        try:
            mro_idx = _root_mro.index(target)
        except ValueError:
            mro_idx = None

        branches: list[Self] = [
            cls.build(base, _root_mro) for base in target.__bases__
        ]

        return cls(
            name=target.__name__,
            id=f"{target.__module__}.{target.__name__}",
            source=target,
            mro_index=mro_idx,
            branches=branches,
        )


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True)
class TypeTreeNode(SimpleTreeNode):
    origin: type = field(compare=False, default=object)

    @property
    def identifier(self):
        return self.origin

    @property
    def display_label(self) -> str:
        return self.origin.__qualname__

    @classmethod
    def from_bases(cls, start: type, *, drop_object: bool = True) -> Self:
        seen: set[type] = set()

        def build(t: type) -> Self:
            if t in seen:
                return cls(name=t.__qualname__, origin=t, branches=())
            seen.add(t)
            bases = [
                b for b in t.__bases__ if not (drop_object and b is object)
            ]
            return cls(
                name=t.__qualname__,
                origin=t,
                branches=tuple(build(b) for b in bases),
            )

        return build(start)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True, slots=True)
class MroTreeNode2:
    """One class in a display tree. Not a lookup cursor."""

    cls: type
    mro_index: int | None = None
    branches: tuple[Self, ...] = ()
    repeated: bool = False

    @property
    def name(self) -> str:
        return self.cls.__qualname__

    @property
    def id(self) -> str:
        return f"{self.cls.__module__}.{self.cls.__qualname__}"

    @property
    def identifier(self) -> type:
        return self.cls

    @property
    def display_label(self) -> str:
        kind = "Protocol" if _is_protocol(self.cls) else "class"
        rank = "" if self.mro_index is None else f"mro={self.mro_index} "
        mark = " (shared)" if self.repeated else ""
        return f"{rank}{self.name} <{kind}>{mark}"


def _is_protocol(cls: type) -> bool:
    try:
        return cls is not Protocol and issubclass(cls, Protocol)
    except TypeError:
        return False


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True)
class SubclassTreeNode(SimpleTreeNode):
    """Represent an Inheritance Graph walking downwards via __subclasses__."""

    cls: type = field(default=object, compare=False)
    registry_id: str | None = None

    @property
    def identifier(self) -> type:
        return self.cls

    @property
    def display_label(self) -> str:
        """Append the registry ID to the visual label if it exists."""
        if self.registry_id:
            return f"{self.name} [cyan]({self.registry_id})[/]"
        return f"[dim]{self.name} (unregistered)[/]"

    @classmethod
    def create(
        cls, target: type, registry: dict[str, type] | None = None
    ) -> Self:
        """Recursively build the tree downward through subclasses."""

        # Capture the registry from the root target on the first pass
        if registry is None:
            registry = getattr(target, "_registry", {})

        # Reverse lookup: find if this class exists in the registry
        reg_id = next((k for k, v in registry.items() if v is target), None)

        branches: Sequence[Self] = [
            cls.create(sub, registry) for sub in target.__subclasses__()
        ]

        return cls(
            name=target.__name__,
            id=f"{target.__module__}.{target.__name__}",
            cls=target,
            registry_id=reg_id,
            branches=branches,
        )
