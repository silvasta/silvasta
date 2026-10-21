"""
Detect Abstract System Tree with Scan from Paths

-
"""

import ast
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from ...port.tree import ApiStyle, AstKind
from ..tree._ast import (
    AstConfig,
    AstExtractionConfig,
    AstOptions,
    AstTreeNode,
    AstTreeNodeG3,
    AstTreeNodeG45,
)
from ._render import format_api

__all__ = [
    "AstVisitor",
    "extract_ast_tree",
    "AstExtractor",
]

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### G420
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


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
        parent.branches = (  # ty:ignore
            *parent.branches,
            current,
        )  # immutable update
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
        parent.branches = (*parent.branches, func_node)  # ty:ignore


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### G3
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def extract_ast_tree(path: Path, config: AstConfig) -> AstTreeNodeG3 | None:
    """Parses a Python file and returns an AstTreeNode tree."""
    if path.suffix not in {".py", ".pyi"}:
        return None

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError, UnicodeDecodeError, OSError:
        return None

    # Helper to recursively build the tree
    def _build_node(node: ast.AST, depth: int) -> list[AstTreeNodeG3]:
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

                docstring = (
                    ast.get_docstring(child)
                    if config.include_docstrings
                    else None
                )

                sub_branches = _build_node(child, depth + 1)

                _ast = AstTreeNodeG3(
                    name=child.name,
                    id=f"{getattr(node, 'name', 'module')}.{child.name}",
                    branches=sub_branches,
                    kind=kind,
                    signature=sig,
                    docstring=docstring,
                    lineno=child.lineno,
                )
                branches.append(_ast)

        return branches

    return AstTreeNodeG3(
        name=path.name,
        id=str(path),
        branches=_build_node(tree, depth=1),
        kind="module",
        docstring=ast.get_docstring(tree)
        if config.include_docstrings
        else None,
    )


@dataclass(frozen=True, slots=True)
class AstExtractor:
    options: AstOptions = AstOptions()
    style: ApiStyle = ApiStyle.COMPACT

    # ----- public API -----

    def extract_tree(self, path: Path) -> AstTreeNodeG45 | None:
        if path.suffix not in {".py", ".pyi"}:
            return None
        try:
            source = path.read_text(encoding="utf-8")
            module = ast.parse(source, filename=str(path))
        except (SyntaxError, UnicodeDecodeError, OSError) as exc:
            logger.debug("AST skip {}: {}", path, exc)
            return None
        return self._module_node(module, path)

    def extract_text(self, path: Path) -> str | None:
        tree = self.extract_tree(path)
        if tree is None:
            return None
        return format_api(tree, self.style, self.options)

    def __call__(self, path: Path) -> str:
        """FileScan-compatible: always return str."""
        text = self.extract_text(path)
        if text is None:
            return f"# skipped: {path.name}\n"
        return text

    # ----- build tree -----

    def _module_node(self, module: ast.Module, path: Path) -> AstTreeNodeG45:
        opt = self.options
        doc = (
            ast.get_docstring(module) if opt.include_module_docstring else None
        )
        children = tuple(self._iter_body(module.body, qualprefix="", depth=0))
        return AstTreeNodeG45(
            name=path.name,
            kind=AstKind.MODULE,
            qualname=path.stem,
            docstring=doc,
            lineno=1,
            branches=children,
        )

    def _iter_body(
        self,
        body: list[ast.stmt],
        qualprefix: str,
        depth: int,
    ) -> Iterator[AstTreeNodeG45]:
        opt = self.options
        if depth > opt.max_depth:
            return

        for stmt in body:
            match stmt:
                case ast.ClassDef() as node:
                    if not self._include_name(node.name):
                        continue
                    yield self._class_node(node, qualprefix, depth)

                case ast.FunctionDef() | ast.AsyncFunctionDef() as node:
                    if depth > 0 and not opt.include_methods:
                        continue
                    if not self._include_name(node.name):
                        continue
                    yield self._func_node(node, qualprefix, depth)

                case ast.Assign() | ast.AnnAssign() if (
                    opt.include_assignments and depth == 0
                ):
                    if (n := self._assign_node(stmt, qualprefix)) is not None:
                        yield n

                case _:
                    continue

    def _include_name(self, name: str) -> bool:
        opt = self.options
        if name in opt.include_dunder:
            return True
        if opt.public_only and name.startswith("_"):
            return False
        return True

    def _class_node(
        self, node: ast.ClassDef, qualprefix: str, depth: int
    ) -> AstTreeNodeG45:
        bases = ", ".join(ast.unparse(b) for b in node.bases)
        qual = f"{qualprefix}.{node.name}" if qualprefix else node.name
        return AstTreeNodeG45(
            name=node.name,
            kind=AstKind.CLASS,
            qualname=qual,
            signature=f"{node.name}({bases})" if bases else node.name,
            decorators=tuple(ast.unparse(d) for d in node.decorator_list),
            docstring=ast.get_docstring(node)
            if self.options.include_docstrings
            else None,
            public=self._include_name(node.name),
            lineno=node.lineno,
            branches=tuple(
                self._iter_body(node.body, qualprefix=qual, depth=depth + 1)
            )
            if self.options.include_nested_classes
            or self.options.include_methods
            else (),
        )

    def _func_node(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        qualprefix: str,
        depth: int,
    ) -> AstTreeNodeG45:
        qual = f"{qualprefix}.{node.name}" if qualprefix else node.name
        kind = (
            AstKind.ASYNC_DEF
            if isinstance(node, ast.AsyncFunctionDef)
            else AstKind.DEF
        )
        args = ast.unparse(node.args)
        ret = ast.unparse(node.returns) if node.returns else None
        doc = (
            ast.get_docstring(node)
            if self.options.include_docstrings
            else None
        )
        return AstTreeNodeG45(
            name=node.name,
            kind=kind,
            qualname=qual,
            signature=f"{node.name}({args})",
            returns=ret,
            decorators=tuple(ast.unparse(d) for d in node.decorator_list),
            docstring=doc,
            public=self._include_name(node.name),
            lineno=node.lineno,
            branches=(),  # depth cap handles nested defs if you open that later
        )

    def _assign_node(
        self, stmt: ast.Assign | ast.AnnAssign, qualprefix: str
    ) -> AstTreeNodeG45 | None:
        # minimal: only simple Name targets
        names: list[str] = []
        if isinstance(stmt, ast.AnnAssign) and isinstance(
            stmt.target, ast.Name
        ):
            names = [stmt.target.id]
        elif isinstance(stmt, ast.Assign):
            names = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
        if not names:
            return None
        name = names[0]
        if not self._include_name(name):
            return None
        qual = f"{qualprefix}.{name}" if qualprefix else name
        ann = ""
        if isinstance(stmt, ast.AnnAssign) and stmt.annotation:
            ann = ast.unparse(stmt.annotation)
        return AstTreeNodeG45(
            name=name,
            kind=AstKind.ASSIGN,
            qualname=qual,
            signature=f"{name}: {ann}" if ann else name,
            lineno=stmt.lineno,
            branches=(),
        )
