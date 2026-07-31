import ast
from dataclasses import dataclass, field
from enum import StrEnum, auto
from pathlib import Path

from ..tree import SimpleTreeNode


@dataclass(frozen=True)
class AstTreeNode(SimpleTreeNode):
    """Represents Python code hierarchy. Fully compatible with existing tree utils."""

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


# def build_ast_tree(
#     path: Path, config: "AstExtractionConfig | None" = None
# ) -> AstTreeNode | None:
#     """Public convenience function (imported from scanner._ast)."""
#     from ..scanner._ast import build_ast_tree as _build
#
#     return _build(path, config)

"""Clean AST extraction with tree output.

Replaces the old ast_api_extractor. Builds semantic AstTreeNodes.
"""

__all__ = [
    "AstExtractionConfig",
    "AstTreeNode",
    "build_ast_tree",
    "render_ast_tree",
]


@dataclass(frozen=True)
class AstExtractionConfig:
    public_only: bool = True
    include_dunder: frozenset[str] = frozenset({"__init__", "__call__"})
    include_module_docstring: bool = True
    include_class_docstring: bool = True
    max_docstring_lines: int | None = 3
    max_depth: int = 3
    include_assignments: bool = False


class AstVisitor(ast.NodeVisitor):
    def __init__(self, config: AstExtractionConfig):
        self.config = config
        self.stack: list[AstTreeNode] = []
        self.root: AstTreeNode | None = None

    def _is_public(self, name: str) -> bool:
        if name in self.config.include_dunder:
            return True
        if self.config.public_only and name.startswith("_"):
            return False
        return True

    def _make_node(
        self,
        kind: str,
        name: str,
        signature: str,
        docstring: str | None = None,
        lineno: int | None = None,
        decorators: tuple[str, ...] = (),
    ) -> AstTreeNode:
        qualname = ".".join(n.name for n in self.stack if n.name) + f".{name}"
        qualname = qualname.strip(".")

        return AstTreeNode(
            name=name,
            kind=kind,
            qualname=qualname,
            signature=signature,
            docstring=docstring,
            lineno=lineno,
            is_public=self._is_public(name),
            decorators=decorators,
            branches=[],
        )

    def visit_Module(self, node: ast.Module) -> None:
        doc = (
            ast.get_docstring(node)
            if self.config.include_module_docstring
            else None
        )
        root = self._make_node(
            kind="module",
            name=node.__class__.__name__,  # or filename
            signature="module",
            docstring=doc,
            lineno=1,
        )
        self.root = root
        self.stack.append(root)
        self.generic_visit(node)
        self.stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if len(self.stack) > self.config.max_depth:
            return

        bases = ", ".join(ast.unparse(b) for b in node.bases)
        signature = (
            f"class {node.name}({bases})" if bases else f"class {node.name}"
        )

        doc = (
            ast.get_docstring(node)
            if self.config.include_class_docstring
            else None
        )
        if doc and self.config.max_docstring_lines:
            doc = "\n".join(doc.split("\n")[: self.config.max_docstring_lines])

        current = self._make_node(
            kind="class",
            name=node.name,
            signature=signature,
            docstring=doc,
            lineno=node.lineno,
            decorators=tuple(ast.unparse(d) for d in node.decorator_list),
        )

        parent = self.stack[-1]
        parent.branches = (*parent.branches, current)  # immutable update
        self.stack.append(current)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function("function", node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function("async_function", node)

    def _visit_function(
        self, kind: str, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        if len(self.stack) > self.config.max_depth:
            return
        if not self._is_public(node.name):
            return

        sig = ast.unparse(node.args)
        returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
        prefix = "async def" if kind == "async_function" else "def"
        signature = f"{prefix} {node.name}({sig}){returns}"

        doc = ast.get_docstring(node)
        if doc and self.config.max_docstring_lines:
            doc = "\n".join(doc.split("\n")[: self.config.max_docstring_lines])

        func_node = self._make_node(
            kind=kind,
            name=node.name,
            signature=signature,
            docstring=doc,
            lineno=node.lineno,
            decorators=tuple(ast.unparse(d) for d in node.decorator_list),
        )

        parent = self.stack[-1]
        parent.branches = (*parent.branches, func_node)


def build_ast_tree(
    path: Path, config: AstExtractionConfig | None = None
) -> AstTreeNode | None:
    if path.suffix not in {".py", ".pyi"}:
        return None

    config = config or AstExtractionConfig()
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        visitor = AstVisitor(config)
        visitor.visit(tree)
        return visitor.root
    except SyntaxError, UnicodeDecodeError, OSError:
        return AstTreeNode(
            name=path.name,
            kind="error",
            signature=f"# Failed to parse {path.name}",
        )


def render_ast_tree(
    node: AstTreeNode, style: str = "compact", indent: str = "  "
) -> str:
    """Render tree in different styles. Extend as needed."""
    lines: list[str] = []

    def _recurse(n: AstTreeNode, depth: int = 0) -> None:
        prefix = indent * depth
        lines.append(f"{prefix}{n.display_label}")
        if n.docstring and style != "signatures_only":
            doc_prefix = prefix + indent
            lines.append(f'{doc_prefix}"""{n.docstring}"""')
        for child in n.branches:
            if isinstance(child, AstTreeNode):
                _recurse(child, depth + 1)

    _recurse(node)
    return "\n".join(lines)


class ScanMode(StrEnum):
    RAW = auto()
    API = auto()
    AST_TREE = auto()  # new
    AST_COMPACT = auto()  # new


class FileScnner:
    scan_mode: ScanMode
    ast_config: AstExtractionConfig = field(
        default_factory=AstExtractionConfig
    )

    def extract(self, path: Path) -> str | AstTreeNode | None:
        if self.scan_mode in (ScanMode.AST_TREE, ScanMode.AST_COMPACT):
            tree = build_ast_tree(path, self.ast_config)
            if self.scan_mode == ScanMode.AST_COMPACT:
                return render_ast_tree(tree, style="compact") if tree else None
            return tree
        # ... existing RAW / old API logic
