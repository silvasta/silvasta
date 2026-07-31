# sstcore/utils/tree/_nodes.py  (addition)
# or scanner/_ast.py if you want scanner-local types

import ast
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import StrEnum, auto
from pathlib import Path

from loguru import logger

from sstcore.utils import FolderScanner

from ..tree import SimpleTreeNode
from ._file import FileExtractor, raw_content_extractor


class AstKind(StrEnum):
    MODULE = auto()
    CLASS = auto()
    DEF = auto()
    ASYNC_DEF = auto()
    ASSIGN = auto()  # optional module-level


@dataclass(frozen=True)
class AstTreeNode(SimpleTreeNode):
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


class ScanMode(StrEnum):
    RAW = auto()
    API = auto()  # formatted API skeleton text


class ApiStyle(StrEnum):
    COMPACT = auto()  # def name(...):\n    """doc"""\n    ...
    STUB = auto()  # .pyi-ish
    # MARKDOWN later if summary machine doesn't already wrap


# sstcore/utils/scanner/_ast.py
"""AST → Api tree → formatted text."""


@dataclass(frozen=True, slots=True)
class AstExtractor:
    options: AstOptions = AstOptions()
    style: ApiStyle = ApiStyle.COMPACT

    # ----- public API -----

    def extract_tree(self, path: Path) -> AstTreeNode | None:
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

    def _module_node(self, module: ast.Module, path: Path) -> AstTreeNode:
        opt = self.options
        doc = (
            ast.get_docstring(module) if opt.include_module_docstring else None
        )
        children = tuple(self._iter_body(module.body, qualprefix="", depth=0))
        return AstTreeNode(
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
    ) -> Iterator[AstTreeNode]:
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
    ) -> AstTreeNode:
        qual = f"{qualprefix}.{node.name}" if qualprefix else node.name
        bases = ", ".join(ast.unparse(b) for b in node.bases)
        sig = f"{node.name}({bases})" if bases else node.name
        children: tuple[AstTreeNode, ...] = ()
        if self.options.include_nested_classes or self.options.include_methods:
            children = tuple(
                self._iter_body(node.body, qualprefix=qual, depth=depth + 1)
            )
        return AstTreeNode(
            name=node.name,
            kind=AstKind.CLASS,
            qualname=qual,
            signature=sig,
            decorators=tuple(ast.unparse(d) for d in node.decorator_list),
            docstring=ast.get_docstring(node)
            if self.options.include_docstrings
            else None,
            public=self._include_name(node.name),
            lineno=node.lineno,
            branches=children,
        )

    def _func_node(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        qualprefix: str,
        depth: int,
    ) -> AstTreeNode:
        qual = f"{qualprefix}.{node.name}" if qualprefix else node.name
        kind = (
            AstKind.ASYNC_DEF
            if isinstance(node, ast.AsyncFunctionDef)
            else AstKind.DEF
        )
        args = ast.unparse(node.args)
        ret = ast.unparse(node.returns) if node.returns else None
        return AstTreeNode(
            name=node.name,
            kind=kind,
            qualname=qual,
            signature=f"{node.name}({args})",
            returns=ret,
            decorators=tuple(ast.unparse(d) for d in node.decorator_list),
            docstring=ast.get_docstring(node)
            if self.options.include_docstrings
            else None,
            public=self._include_name(node.name),
            lineno=node.lineno,
            branches=(),  # depth cap handles nested defs if you open that later
        )

    def _assign_node(
        self, stmt: ast.Assign | ast.AnnAssign, qualprefix: str
    ) -> AstTreeNode | None:
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
        return AstTreeNode(
            name=name,
            kind=AstKind.ASSIGN,
            qualname=qual,
            signature=f"{name}: {ann}" if ann else name,
            lineno=stmt.lineno,
            branches=(),
        )


def format_api(
    root: AstTreeNode,
    style: ApiStyle = ApiStyle.COMPACT,
    options: AstOptions | None = None,
) -> str:
    options = options or AstOptions()
    match style:
        case ApiStyle.COMPACT:
            return "\n".join(_format_compact(root, options))
        case ApiStyle.STUB:
            return "\n".join(_format_stub(root, options))


def _format_compact(
    node: AstTreeNode, opt: AstOptions, indent: int = 0
) -> list[str]:
    sp = "    " * indent
    lines: list[str] = []

    if node.kind is AstKind.MODULE:
        if opt.include_module_docstring and node.docstring:
            lines.append(f'"""{node.docstring}"""')
            lines.append("")
        for child in node.branches:
            lines.extend(_format_compact(child, opt, indent=0))
            lines.append("")
        return lines

    if node.kind is AstKind.CLASS:
        lines.append(f"{sp}class {node.signature}:")
    elif node.kind is AstKind.ASYNC_DEF:
        ret = f" -> {node.returns}" if node.returns else ""
        lines.append(f"{sp}async def {node.signature}{ret}:")
    elif node.kind is AstKind.DEF:
        ret = f" -> {node.returns}" if node.returns else ""
        lines.append(f"{sp}def {node.signature}{ret}:")
    elif node.kind is AstKind.ASSIGN:
        lines.append(f"{sp}{node.signature}")
        return lines

    if opt.include_docstrings and node.docstring:
        # single-line prefer; multi-line keep simple
        doc = node.docstring.replace("\n", f"\n{sp}    ")
        lines.append(f'{sp}    """{doc}"""')

    if node.branches:
        for child in node.branches:
            lines.extend(_format_compact(child, opt, indent=indent + 1))
    else:
        lines.append(f"{sp}    ...")

    return lines


def _format_stub(
    node: AstTreeNode, opt: AstOptions, indent: int = 0
) -> list[str]:
    # same structure; ellipsis bodies, no nested implementation detail
    # can share helpers with compact later
    raise NotImplementedError


# _file.py (revised core)


class _ScanMode(StrEnum):
    RAW = auto()
    API = auto()


@dataclass
class FileScanner:
    files: list[Path]
    local_root: Path
    scan_mode: ScanMode = ScanMode.RAW
    ast_options: AstOptions = field(default_factory=AstOptions)
    api_style: ApiStyle = ApiStyle.COMPACT

    def splitted_files(self):
        pass

    def file_scan(self) -> Iterator[tuple[str, Path]]:
        extractor = self._extractor()
        for read_path, show_path in self.splitted_files():
            try:
                text = extractor(read_path)
            except (UnicodeDecodeError, OSError) as error:
                logger.debug("skip {}: {}", read_path, error)
                continue
            if text is None:
                continue
            yield text, show_path

    def _extractor(self) -> FileExtractor:
        match self.scan_mode:
            case ScanMode.RAW:
                return raw_content_extractor
            case ScanMode.API:
                return AstExtractor(self.ast_options, self.api_style)

    def ast_forest(self) -> list[AstTreeNode]:
        """Optional: trees for TUI / multi-file overview."""
        ext = AstExtractor(self.ast_options, self.api_style)
        trees: list[AstTreeNode] = []
        for read_path, _show_path in self.splitted_files():
            if (t := ext.extract_tree(read_path)) is not None:
                # show_path.name as label if you prefer relative display
                trees.append(t)
        return trees


def ast_tree(self) -> AstTreeNode:
    modules = self.ast_forest()
    return AstTreeNode(
        name=self.local_root.name,  # or scan_root
        kind=AstKind.MODULE,
        qualname="",
        branches=tuple(modules),
    )


@dataclass
class AstScanner:
    """Folder walk + AST extract. CLI entry for --mode api / tree view."""

    folder: FolderScanner
    options: AstOptions = field(default_factory=AstOptions)
    style: ApiStyle = ApiStyle.COMPACT

    def files(self) -> list[Path]:
        return self.folder.get_files()

    def tree(self) -> AstTreeNode:
        ext = AstExtractor(self.options, self.style)
        branches = []
        for path in self.files():
            if path.suffix not in {".py", ".pyi"}:
                continue
            if (node := ext.extract_tree(path)) is not None:
                branches.append(node)
        return AstTreeNode(
            name=self.folder.scan_root.name,
            kind=AstKind.MODULE,
            branches=tuple(branches),
        )

    def summary_scanner(self) -> FileScanner:
        return FileScanner(
            files=self.files(),
            local_root=self.folder.scan_root,
            scan_mode=ScanMode.API,
            ast_options=self.options,
            api_style=self.style,
        )


# sketch — typer/argparse/click, whatever you use
def scan(
    root: Path,
    mode: ScanMode = ScanMode.RAW,
    api_style: ApiStyle = ApiStyle.COMPACT,
    public_only: bool = True,
    include_docs: bool = True,
    max_depth: int = 2,
    output: Path | None = None,
    show_tree: bool = False,
):
    folder = FolderScanner(root)
    options = AstOptions(
        public_only=public_only,
        include_docstrings=include_docs,
        max_depth=max_depth,
    )
    if show_tree and mode is ScanMode.API:
        _tree = AstScanner(folder, options, api_style).tree()
        # render_tui(tree)  # existing SimpleTreeNode UI
        return

    files = folder.get_files()
    _scanner = FileScanner(files, root, mode, options, api_style)
    # if output:
    #     SummaryFile.with_scanner(output, files, root, mode).write()
    # note: with_scanner must take options through — see below
