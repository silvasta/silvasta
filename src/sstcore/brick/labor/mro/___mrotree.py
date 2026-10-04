"""
Tree Printer

- temporary module
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, Self

from rich.tree import Tree

from ....port.link._render import _load_printer


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


class Printy(_load_printer()):
    def bases_tree(
        self, cls: type, *, expand_shared: bool = False
    ) -> MroTreeNode2:
        rank = {base: i for i, base in enumerate(cls.__mro__)}
        seen: set[type] = set()

        def walk(current: type) -> MroTreeNode2:
            children: list[MroTreeNode2] = []
            for base in current.__bases__:
                if base in seen and not expand_shared:
                    children.append(
                        MroTreeNode2(
                            cls=base, mro_index=rank.get(base), repeated=True
                        )
                    )
                    continue
                seen.add(base)
                children.append(walk(base))
            return MroTreeNode2(
                cls=current,
                mro_index=rank.get(current),
                branches=tuple(children),
            )

        seen.add(cls)
        tree = walk(cls)
        self(tree)
        return tree

    def mro_list_tree(self, cls: type) -> Tree:
        """Lame..."""
        root = Tree(f"{cls.__qualname__}.__mro__")
        for i, t in enumerate(cls.__mro__):
            root.add(f"{i:>2}  {t.__module__}.{t.__qualname__}")
        self(root)
        return root

    def bases_to_rich(self, cls: type, *, drop_object: bool = True) -> Tree:
        root = Tree(cls.__qualname__)
        seen: set[type] = {cls}

        def add(t: type, branch: Tree) -> None:
            for base in t.__bases__:
                if drop_object and base is object:
                    continue
                label = base.__qualname__
                if base in seen:
                    branch.add(f"{label} ↩")
                    continue
                seen.add(base)
                child = branch.add(label)
                add(base, child)

        add(cls, root)
        self(root)
        return root

    def tree_graph(  # IDEA: MRO display???
        self,
        simple_tree: SimpleTree,
        max_depth: int | None = None,
        root: str = "bold magenta",
        node: str = "by_level",
        guide: str = "bold white",
        hide_root=False,
    ) -> None:
        """Render SimpleTreeNode as nested Rich Tree in Terminal"""

        _node_styles: dict[int, str] = {
            1: "green",
            2: "yellow",
            3: "white",
        }

        def _apply_style(node_label: str, color: str | int = ""):
            if isinstance(color, int):
                color: str = _node_styles.get(color, "red")
            return f"[{color}]{node_label}[/]" if color else node_label

        visual_tree = Tree(
            label=_apply_style(simple_tree.name, color=root),
            guide_style=guide,
            hide_root=hide_root,
        )

        def build_branch(
            tree_node: SimpleTree,
            current_branch: Tree,
            current_depth: int,
        ):
            if max_depth is not None and current_depth >= max_depth:
                return

            nonlocal node
            color: str | int = current_depth if node == "by_level" else node

            for branch in tree_node.branches:
                child_label: str = _apply_style(
                    branch.display_label, color=color
                )
                child_branch: Tree = current_branch.add(child_label)

                build_branch(branch, child_branch, current_depth + 1)

        build_branch(simple_tree, visual_tree, current_depth=1)

        self(visual_tree)


printer = Printy()


def test_mro_tree():
    class A:
        pass

    class B(A):
        pass

    class C(A):
        pass

    class D(B, C):
        pass

    # 1. Build the Node Tree
    mro_tree = MroTreeNode1.build(D)

    # 2. Print it using your existing TreePrinter
    printer.tree_graph(simple_tree=mro_tree, root="bold cyan", node="by_level")


if __name__ == "__main__":
    test_mro_tree()
