"""
Scan File Content

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "FileScan",
    "ScanMode",
    "FileScanner",
]

import ast
from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path
from typing import Protocol

from loguru import logger

from ...utils.path import PathGuard


class ScanMode(StrEnum):
    RAW = auto()
    API = auto()

    @property
    def extractor(self) -> FileScan:
        match self:
            case ScanMode.API:
                return ast_api_extractor
            case ScanMode.RAW:
                return raw_content_extractor


class FileScan(Protocol):
    def __call__(self, path: Path) -> str: ...


@dataclass
class FileScanner:
    files: list[Path]
    local_root: Path
    scan_mode: ScanMode = ScanMode.RAW

    def splitted_files(self) -> Iterator[tuple[Path, Path]]:
        for target in self.files:  # LATER: make this directly in PathGuard
            read_path, show_path = PathGuard.split(target, self.local_root)
            if not read_path.is_file():
                continue
            yield read_path, show_path

    def file_scan(self) -> Iterator[tuple[str, Path]]:
        """Scan all files by mode, skip fails and yield extracted results"""

        for read_path, show_path in self.splitted_files():
            try:
                text: str = self.scan_mode.extractor(read_path)
            except (UnicodeDecodeError, OSError) as error:
                logger.debug(f"skip {read_path}: {error}")

            yield text, show_path


def raw_content_extractor(path: Path) -> str:
    """Default: Just read the file contents."""
    return path.read_text(encoding="utf-8")


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### AST Ideas
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def ast_api_extractor(path: Path) -> str:
    """Reads Python files and extracts the API skeleton. Returns raw text for others."""
    if path.suffix not in {".py", ".pyi"}:
        # Fallback for non-python files (or return an empty string if you prefer)
        return (
            f"<!-- AST Skeleton skipped for non-python file: {path.name} -->\n"
        )

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return f"# Failed to parse syntax for {path.name}\n"

    lines = []
    for item in tree.body:
        if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
            lines.append(f'"""{item.value.value}"""\n')
        elif isinstance(
            item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            if not item.name.startswith("_") or item.name == "__init__":
                docstring = ast.get_docstring(item)
                prefix = "class " if isinstance(item, ast.ClassDef) else "def "
                lines.append(f"{prefix}{item.name}(...):")
                if docstring:
                    lines.append(f'    """{docstring}"""')
                lines.append("    ...")

    return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class ApiDoc:
    text: str


@dataclass(frozen=True, slots=True)
class ApiNode:
    kind: str  # module | class | def | async def | assign?
    name: str
    qualname: str  # "Class.method"
    signature: str  # unparsed args / bases
    returns: str | None
    decorators: tuple[str, ...]
    docstring: str | None
    public: bool
    lineno: int
    children: tuple[ApiNode, ...] = ()


@dataclass
class AstApiOptions:
    public_only: bool = True
    include_dunder: frozenset[str] = frozenset({"__init__"})
    include_module_docstring: bool = True
    include_methods: bool = True
    include_nested_classes: bool = True
    include_assignments: bool = False  # module-level constants / TypeAlias
    max_depth: int = 2  # module=0, class=1, method=2


@dataclass
class AstExtractionConfig:
    include_private: bool = False
    include_dunder: bool = False  # __init__, __call__, etc.
    include_module_docstring: bool = True
    include_class_docstring: bool = True
    max_docstring_lines: int | None = None
    show_signatures: bool = False  # future: use inspect.signature logic
    include_type_hints: bool = False


def _is_public(name: str, options: AstApiOptions) -> bool:
    if name in options.include_dunder:
        return True
    if options.public_only and name.startswith("_"):
        return False
    return True


class ApiStyle(StrEnum):
    COMPACT = auto()  # name(...): / docstring / ...
    STUB = auto()  # closer to .pyi
    MARKDOWN = auto()  # ### headings


def format_api(
    nodes: list[ApiNode], style: ApiStyle = ApiStyle.COMPACT
) -> str:
    match style:
        case ApiStyle.COMPACT:
            pass  # return _format_compact(nodes)
        case ApiStyle.STUB:
            pass  # return _format_stub(nodes)


def _func_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = ast.unparse(node.args)
    ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {node.name}({args}){ret}"


def _class_signature(node: ast.ClassDef) -> str:
    bases = ", ".join(ast.unparse(b) for b in node.bases)
    return f"class {node.name}({bases})" if bases else f"class {node.name}"


def _ast_api_extractor(
    path: Path, options: AstApiOptions | None = None
) -> str | None:
    if path.suffix not in {".py", ".pyi"}:
        return None
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError, UnicodeDecodeError, OSError:
        return None
    nodes = iter_api_nodes(tree, options or AstApiOptions())  # ty:ignore
    return format_api(nodes, ApiStyle.COMPACT)


# class ScanMode(StrEnum):
#     RAW = auto()
#     API = auto()
#     API_STUB = auto()     # .pyi-like
#     SIGNATURES = auto()   # names + sigs, no docstrings
#     HEADERS = auto()      # first N lines / module docstring only

# @dataclass
# class FileScanner:
#     files: list[Path]
#     local_root: Path
#     scan_mode: ScanMode = ScanMode.RAW
#     # IMPORTANT:
#     api_options: AstApiOptions = field(default_factory=AstApiOptions)
#
#     def extract(self, path: Path) -> str | None:
#         if self.scan_mode is ScanMode.API:
#             return ast_api_extractor(path, self.api_options)
#         return raw_content_extractor(path)


class ApiVisitor(ast.NodeVisitor):
    def __init__(self, config: AstExtractionConfig):
        self.config = config
        self.lines: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        if self._should_include(node):  # ty:ignore
            ...
        self.generic_visit(node)


class ExtractionLevel(StrEnum):
    SIGNATURES_ONLY = "signatures"
    WITH_DOCSTRINGS = "docstrings"
    COMPACT = "compact"
    FULL_PUBLIC_API = "full"
