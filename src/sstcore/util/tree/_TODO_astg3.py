import ast
from dataclasses import dataclass
from pathlib import Path

from ._nodes import SimpleTreeNode


# sstcore/utils/scanner/_ast_config.py
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
class AstTreeNode(SimpleTreeNode):
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


# sstcore/utils/scanner/_ast_extractor.py
def extract_ast_tree(path: Path, config: AstConfig) -> AstTreeNode | None:
    """Parses a Python file and returns an AstTreeNode tree."""
    if path.suffix not in {".py", ".pyi"}:
        return None

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError, UnicodeDecodeError, OSError:
        return None

    # Helper to recursively build the tree
    def _build_node(node: ast.AST, depth: int) -> list[AstTreeNode]:
        if depth > config.max_depth:
            return []

        branches = []
        for child in ast.iter_child_nodes(node):
            if isinstance(
                child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                if not config.is_target_public(child.name):
                    continue

                # Determine signature and kind
                if isinstance(child, ast.ClassDef):
                    kind = "class"
                    bases = ", ".join(ast.unparse(b) for b in child.bases)
                    sig = f"({bases})" if bases else ""
                else:
                    kind = (
                        "async function"
                        if isinstance(child, ast.AsyncFunctionDef)
                        else "function"
                    )
                    args = ast.unparse(child.args)
                    ret = (
                        f" -> {ast.unparse(child.returns)}"
                        if child.returns
                        else ""
                    )
                    sig = f"({args}){ret}"

                # Extract docstring safely
                docstring = (
                    ast.get_docstring(child)
                    if config.include_docstrings
                    else None
                )

                # Recursively parse children (methods inside classes, nested funcs)
                sub_branches = _build_node(child, depth + 1)

                branches.append(
                    AstTreeNode(
                        name=child.name,
                        id=f"{getattr(node, 'name', 'module')}.{child.name}",
                        branches=sub_branches,
                        kind=kind,
                        signature=sig,
                        docstring=docstring,
                        lineno=child.lineno,
                    )
                )

            # NOTE: You can add `ast.AnnAssign` or `ast.Assign` here if config.include_assignments is True

        return branches

    # Build the root module node
    module_doc = ast.get_docstring(tree) if config.include_docstrings else None
    return AstTreeNode(
        name=path.name,
        id=str(path),
        branches=_build_node(tree, depth=1),
        kind="module",
        docstring=module_doc,
    )


# sstcore/utils/scanner/_ast_render.py
def render_api_compact(node: AstTreeNode, indent: int = 0) -> str:
    """Renders the AST Tree into a compact text format."""
    lines = []
    spacer = "    " * indent

    if node.kind == "module":
        if node.docstring:
            lines.append(f'"""{node.docstring}"""\n')
    else:
        prefix = (
            "class "
            if node.kind == "class"
            else ("async def " if "async" in node.kind else "def ")
        )
        lines.append(f"{spacer}{prefix}{node.name}{node.signature}:")
        if node.docstring:
            lines.append(f'{spacer}    """{node.docstring}"""')

        # If it has no branches (e.g., empty class or function), add ellipsis
        if not node.branches and node.kind != "module":
            lines.append(f"{spacer}    ...")

    for branch in node.branches:
        lines.append(
            render_api_compact(
                branch, indent + (1 if node.kind != "module" else 0)
            )
        )

    return "\n".join(lines)
