"""
printer - quick helper copied temporary into port

- temporary module
"""

__all__: list[str] = [
    "printer",
]

from collections.abc import Iterable
from contextlib import contextmanager

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.tree import Tree

from ..calling import Stringable
from ..tree import SimpleTree
from .___tree import MroTreeNode1, MroTreeNode2

console = Console()


class QuickPrinter:
    def __call__(self, *args, **kwargs):
        console.print(*args, **kwargs)

    def lines(self, target: Iterable[Stringable], /):
        match target:
            case dict():
                _lines = (f"{k}: {v}" for k, v in target.items())
            case _:
                _lines = (str(i) for i in target)
        self("\n".join(_lines))

    @contextmanager
    def topic(self, title, /):
        self.panel(f"Start of: {title}", frame="green", title=title)
        try:
            yield
        finally:
            self.line()

    #  LINE: -- Layouts -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def section(self, title, content):
        self.panel(title, frame="yellow")
        self(content)

    def panel(self, content, /, text="bold white", title=None, frame="cyan"):
        panel = Panel(
            renderable=content,
            style=text,
            title=f"[bold white]{title}[/]" if title else None,
            title_align="right",
            border_style=frame,
        )
        self(panel)

    def header(self, content, /, title=None, frame: str = "cyan") -> None:
        self.panel(content, frame=frame, title=title)

    def line(self, char="-- --- --", color="red"):
        self(Rule(style=color, characters=char))

    #  LINE: -- Specialized -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def vars(self, target, /):
        self(vars(target), title=f"vars({clsname(target)})")

    def repr(self, target, /):
        self(repr(target))

    def debug(
        self,
        target: dict,
        /,
        header="Dict Inspection",
        show_type: bool | tuple[bool, bool] = (True, True),
        style="yellow",
    ) -> None:
        """Render colorful Debug Dict, optional with Key or Value Type"""
        if header:
            self.header(header, title="Dict Inspection", frame=style)

        table = Table(style=style)

        show_key_type, show_value_type = (
            show_type
            if isinstance(show_type, tuple)
            else (show_type, show_type)
        )

        table.add_column("Key", justify="left", style="green")
        if show_key_type:
            table.add_column("Type Key", justify="center", style="magenta")

        table.add_column("Value", style="blue", justify="left")
        if show_value_type:
            table.add_column("Type Value", style="magenta")

        for key, value in target.items():
            row: list[str] = [
                key,
                *([type(key).__name__] if show_key_type else []),
                str(value),
                *([type(value).__name__] if show_value_type else []),
            ]
            table.add_row(*row)

        self(table)

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


def clsname(target, /, default="") -> str:
    """Extract name from instance or class"""
    default: str = default or type(target).__name__
    return getattr(target, "__name__", default)


printer = QuickPrinter()


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


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
