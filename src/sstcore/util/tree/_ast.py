"""
Generate Abstract System Tree with Nodes from Paths

- PathTreeNode: Represent FileTree built with decomposed Paths
- build_path_tree: Recursively stack folder and files
                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "AstNode",
]

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ...port.tree import AstKind, ASTree
from ..scan._ast import AstVisitor  # WARN: Bad Dependency
from ..tree import SimpleTreeNode


@dataclass(frozen=True)
class AstNode(SimpleTreeNode):
    """Represent Abstract Python Sysntax Tree"""


if TYPE_CHECKING:
    _instance: ASTree = AstNode("ast")
    _class: type[ASTree] = AstNode

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### G420
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

__all__ = [
    "AstExtractionConfig",
    "AstTreeNode",
    "build_ast_tree",
]


@dataclass(frozen=True)
class AstTreeNode(SimpleTreeNode):
    kind: str = "unknown"  # module, class, function, async_function
    qualname: str = ""  # "ModuleName.Class.method"
    signature: str = ""  # "def foo(x: int) -> str" or "class Bar(Base)"
    docstring: str | None = None
    lineno: int | None = None
    is_public: bool = True
    decorators: tuple[str, ...] = ()

    @property
    def display_label(self) -> str:
        """Rich label for TUI, printing, or selection."""
        icon = {
            "module": "📦",
            "class": "🏛️",
            "function": "⚙️",
            "async_function": "⚡",
        }.get(self.kind, "•")

        if self.signature:
            return f"{icon} {self.signature}"
        return f"{icon} {self.kind} {self.name}"

    @property
    def identifier(self):
        return self.qualname or self.name


# MOVE: CONFIG
@dataclass(frozen=True)
class AstExtractionConfig:
    public_only: bool = True
    include_dunder: frozenset[str] = frozenset({"__init__", "__call__"})
    include_module_docstring: bool = True
    include_class_docstring: bool = True
    max_docstring_lines: int | None = 3
    max_depth: int = 3
    include_assignments: bool = False


def build_ast_tree(
    path: Path, config: AstExtractionConfig | None = None
) -> AstTreeNode | None:
    if path.suffix not in {".py", ".pyi"}:
        return None

    config = config or AstExtractionConfig()
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        # AI: this is probably only dependency in this direction
        visitor = AstVisitor(config)  # WARN: Bad Dependency
        visitor.visit(tree)
        return visitor.root
    except SyntaxError, UnicodeDecodeError, OSError:
        return AstTreeNode(
            name=path.name,
            kind="error",
            signature=f"# Failed to parse {path.name}",
        )


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### G3
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


# MOVE: CONFIG
@dataclass(frozen=True)
class AstConfig:
    """Configuration for AST Extraction, easily map-able to CLI flags."""

    public_only: bool = True
    include_dunder: frozenset[str] = frozenset({"__init__", "__call__"})
    include_docstrings: bool = True
    include_assignments: bool = False
    max_depth: int = 3  # module=0, class=1, method=2, nested=3

    def is_target_public(self, name: str) -> bool:
        """Check if a node name should be included based on visibility rules."""
        if name in self.include_dunder:
            return True
        if self.public_only and name.startswith("_"):
            return False
        return True


# sstcore/utils/tree/_nodes.py (Addition)
@dataclass(frozen=True)
class AstTreeNodeG3(SimpleTreeNode):
    """Represent an AST construct (Class, Function, Module)"""

    kind: str = "module"  # 'module', 'class', 'function', 'async function'
    signature: str = ""
    docstring: str | None = None
    lineno: int = 0

    @property
    def display_label(self) -> str:
        """Overrides SimpleTreeNode display for TUI representation"""
        prefix = f"[{self.kind[0].upper()}]"  # e.g., [C] MyClass, [F] my_func
        return f"{prefix} {self.name}{self.signature}"


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### G45
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### G45
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@dataclass(frozen=True)
class AstTreeNodeG45(SimpleTreeNode):
    """API symbol tree: module → class → method/nested class."""

    kind: AstKind = AstKind.MODULE
    qualname: str = ""
    signature: str = ""  # unparsed args / bases
    returns: str | None = None
    decorators: tuple[str, ...] = ()
    docstring: str | None = None
    public: bool = True
    lineno: int = 0
    # name, id, branches come from SimpleTreeNode

    @property
    def display_label(self) -> str:
        """Selector / TUI line."""
        sig = self.signature or self.name
        return (
            f"{self.kind} {sig}" if self.kind != AstKind.MODULE else self.name
        )

    @property
    def identifier(self):
        return self.qualname or self.name


@dataclass(frozen=True, slots=True)
class AstOptions:
    public_only: bool = True
    include_dunder: frozenset[str] = frozenset({"__init__"})
    include_module_docstring: bool = True
    include_docstrings: bool = True
    include_methods: bool = True
    include_nested_classes: bool = True
    include_assignments: bool = False
    max_depth: int = 2  # module=0, class=1, method=2


def ast_tree(self) -> AstTreeNode:
    return AstTreeNode(
        name=self.local_root.name,  # or scan_root
        kind=AstKind.MODULE,
        qualname="",
        branches=tuple(self.ast_forest()),
    )
